import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import aiohttp
from database import Database
from moysklad_api import MoySkladAPI
from config import SHOP_NAME, CURRENCY

app = FastAPI(title="Telegram Shop WebApp")

# Настройка шаблонов и статических файлов
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Маршрут для кэшированных изображений
@app.get("/cache/{cache_key}.jpg")
async def get_cached_image(cache_key: str):
    """Получение кэшированного изображения"""
    cache_path = f"image_cache/{cache_key}.jpg"
    if os.path.exists(cache_path):
        return FileResponse(cache_path, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="Image not found")

# Инициализация компонентов
db = Database()
moysklad = MoySkladAPI()

@app.get("/")
async def catalog_page():
    """Главная страница каталога"""
    try:
        # Получаем все товары для отображения
        products = await moysklad.get_products(limit=1000, offset=0)
        categories = await moysklad.get_categories()
        
        return templates.TemplateResponse("catalog.html", {
            "request": {},
            "products": products,
            "categories": categories
        })
    except Exception as e:
        print(f"Ошибка загрузки каталога: {e}")
        return templates.TemplateResponse("catalog.html", {
            "request": {},
            "products": [],
            "categories": []
        })

# Удаляем дублирующий роут - оставляем только один на строке 295

@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    """Страница корзины"""
    user_id = "demo_user"  # Для веб-версии используем demo_user
    
    cart_items = db.get_cart(user_id)
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "cart_items": cart_items,
        "total": total,
        "shop_name": "Мой Магазин",
        "currency": "₽"
    })

@app.get("/test-cart", response_class=HTMLResponse)
async def test_cart_page(request: Request):
    """Тестовая страница корзины"""
    return templates.TemplateResponse("cart_simple.html", {
        "request": request
    })

@app.post("/api/add-to-cart")
async def add_to_cart(request: Request):
    """API для добавления товара в корзину"""
    data = await request.json()
    
    user_id = data.get('user_id', 'demo_user')
    product_id = data.get('product_id')
    color = data.get('color')  # Добавляем цвет
    size = data.get('size')    # Добавляем размер
    quantity = data.get('quantity', 1)
    
    # Отладочная информация
    print(f"🔍 Добавление в корзину: user_id={user_id}, product_id={product_id}, color={color}, size={size}, quantity={quantity}")
    
    if not product_id:
        raise HTTPException(status_code=400, detail="Product ID required")
    
    # Получаем информацию о товаре
    products = await moysklad.get_products(limit=1000, offset=0)
    product = next((p for p in products if p.get('original_id') == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Проверяем остатки с учетом размера, если указан
    max_stock = product.get('stock', 0)
    if size and product.get('modifications_text'):
        # Парсим строку вида "В наличии: 42-1, 44-0"
        try:
            mods = product['modifications_text'].replace('В наличии: ', '').split(', ')
            size_to_stock = {m.split('-')[0]: int(float(m.split('-')[1])) for m in mods if '-' in m}
            if size in size_to_stock:
                max_stock = size_to_stock[size]
        except Exception:
            pass
    if quantity > max_stock:
        raise HTTPException(status_code=400, detail=f"Недостаточно товара. Доступно: {int(max_stock)}")
    
    # Формируем название товара с цветом и размером
    product_name = product['name']
    if color and size:
        product_name = f"{product['name']} (цвет {color}, размер {size})"
    elif color:
        product_name = f"{product['name']} (цвет {color})"
    elif size:
        product_name = f"{product['name']} (размер {size})"
    
    # Добавляем в корзину
    db.add_to_cart(
        user_id=user_id,
        product_id=f"{product_id}_{color}_{size}" if color and size else f"{product_id}_{size}" if size else product_id,  # Уникальный ID для цвета и размера
        product_name=product_name,
        quantity=quantity,
        price=product['price'],
        size=size,
        color=color,
        image=product.get('image')  # Добавляем изображение
    )
    
    return {"success": True, "message": "Товар добавлен в корзину"}

@app.get("/api/categories")
async def get_categories():
    """Получение списка категорий"""
    try:
        categories = await moysklad.get_categories()
        return {"categories": categories}
    except Exception as e:
        print(f"❌ Ошибка получения категорий: {e}")
        return {"categories": []}

@app.get("/api/products")
async def get_products(limit: int = 50, offset: int = 0, category: str = None):
    """API для получения списка товаров с пагинацией и фильтрацией по категории"""
    # Загружаем больше товаров, чтобы учесть фильтрацию
    load_limit = limit * 3 if category and category != 'all' else limit
    products = await moysklad.get_products(limit=load_limit, offset=offset)
    
    # Фильтруем по категории если указана
    if category and category != 'all':
        original_count = len(products)
        products = [p for p in products if p.get('category') == category]
        print(f"Фильтрация по категории '{category}': из {original_count} найдено {len(products)} товаров")
    
    # Ограничиваем результат до запрошенного лимита (только если не запрашиваем все товары)
    if limit < 1000 and len(products) > limit:
        products = products[:limit]
    
    # Проверяем, есть ли еще товары
    has_more = len(products) == limit
    
    # Если получили 0 товаров, значит больше нет
    if len(products) == 0:
        has_more = False
    
    # Если получили товары, но меньше чем limit, проверяем есть ли еще
    if len(products) > 0 and len(products) < limit:
        # Проверяем, есть ли еще товары, делая дополнительный запрос
        try:
            next_offset = offset + load_limit
            next_products = await moysklad.get_products(limit=10, offset=next_offset)
            
            # Если фильтруем по категории, проверяем есть ли товары этой категории в следующей порции
            if category and category != 'all':
                next_products = [p for p in next_products if p.get('category') == category]
            
            has_more = len(next_products) > 0
            print(f"🔍 Дополнительная проверка: offset={next_offset}, получено={len(next_products)}, has_more={has_more}")
        except Exception as e:
            print(f"⚠️ Ошибка при дополнительной проверке: {e}")
            has_more = False
    
    print(f"API /api/products: limit={limit}, offset={offset}, получено={len(products)}, has_more={has_more}")
    
    return {"products": products, "has_more": has_more}

@app.get("/api/products-with-images")
async def get_products_with_images():
    """API для получения товаров с изображениями"""
    products = await moysklad.get_products(limit=1000, offset=0)
    return {"products": products}

@app.get("/api/categories")
async def get_categories():
    """API для получения списка категорий товаров"""
    try:
        categories = await moysklad.get_categories()
        return {"categories": categories}
    except Exception as e:
        print(f"Ошибка получения категорий: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/categories-with-products")
async def get_categories_with_products():
    """API для получения списка категорий, в которых есть товары"""
    try:
        # Получаем все товары для создания категорий
        products = await moysklad.get_products(limit=1000, offset=0)
        
        # Подсчитываем количество товаров в каждой категории по folder.name
        category_counts = {}
        for product in products:
            # Проверяем, что у товара есть остатки
            if product.get('stock', 0) > 0:
                # Используем category как категорию
                category_name = product.get('category', 'Relealized')
                category_counts[category_name] = category_counts.get(category_name, 0) + 1
        
        # Создаем список категорий с количеством товаров
        categories_with_products = []
        for category_name, count in category_counts.items():
            categories_with_products.append({
                'id': category_name,  # Используем название как ID
                'name': category_name,
                'product_count': count
            })
        
        # Сортируем по количеству товаров (убывание)
        categories_with_products.sort(key=lambda x: x['product_count'], reverse=True)
        
        category_names = [f"{cat['name']}({cat['product_count']})" for cat in categories_with_products]
        print(f"Категории с товарами: {category_names}")
        
        return {"categories": categories_with_products}
    except Exception as e:
        print(f"Ошибка получения категорий с товарами: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/category/{category_id}")
async def get_category_info(category_id: str):
    """API для получения информации о конкретной категории"""
    try:
        category_info = await moysklad.get_category_info(category_id)
        if category_info:
            return {"category": category_info}
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        print(f"Ошибка получения категории: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/cart/{user_id}")
async def get_cart(user_id: str):
    """API для получения корзины пользователя"""
    cart_items = db.get_cart(user_id)
    # Дополнительно отдаем max_stock для каждой позиции (для фронта)
    try:
        products = await moysklad.get_products(limit=1000, offset=0)
        by_id = {p.get('original_id'): p for p in products}
        for item in cart_items:
            base_id = item['product_id']
            size = None
            if '_' in base_id:
                parts = base_id.split('_')
                base_id = parts[0]
                size = parts[1] if len(parts) > 1 else None
            p = by_id.get(base_id)
            max_stock = p.get('stock', 0) if p else 0
            if size and p and p.get('modifications_text'):
                try:
                    mods = p['modifications_text'].replace('В наличии: ', '').split(', ')
                    size_to_stock = {m.split('-')[0]: int(float(m.split('-')[1])) for m in mods if '-' in m}
                    if size in size_to_stock:
                        max_stock = size_to_stock[size]
                except Exception:
                    pass
            item['max_stock'] = int(max_stock)
    except Exception:
        # В случае ошибки просто не добавляем max_stock
        pass

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return {"cart_items": cart_items, "total": total}

@app.post("/api/clear-cart")
async def clear_cart(request: Request):
    """Очистка корзины пользователя"""
    try:
        data = await request.json()
        user_id = data.get("user_id", "demo_user")
        
        db.clear_cart(user_id)
        
        return {"success": True, "message": "Корзина очищена"}
    except Exception as e:
        print(f"Ошибка очистки корзины: {e}")
        return {"success": False, "message": "Ошибка очистки корзины"}

@app.post("/api/update-cart")
async def update_cart(request: Request):
    """API для обновления корзины"""
    data = await request.json()
    user_id = data.get('user_id', 'demo_user')
    product_id = data.get('product_id')  # уже включает размер (product_originalId_size)
    new_quantity = int(data.get('quantity', 1))

    if not product_id:
        raise HTTPException(status_code=400, detail="Product ID required")

    # Вытаскиваем оригинальный id и размер из составного product_id
    base_id = product_id
    size = None
    if '_' in product_id:
        parts = product_id.split('_')
        base_id = parts[0]
        size = parts[1] if len(parts) > 1 else None

    # Получаем товар из источника, чтобы узнать актуальный остаток
    products = await moysklad.get_products(limit=1000, offset=0)
    product = next((p for p in products if p.get('original_id') == base_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Определяем максимум по остатку
    max_stock = product.get('stock', 0)
    if size and product.get('modifications_text'):
        try:
            mods = product['modifications_text'].replace('В наличии: ', '').split(', ')
            size_to_stock = {m.split('-')[0]: int(float(m.split('-')[1])) for m in mods if '-' in m}
            if size in size_to_stock:
                max_stock = size_to_stock[size]
        except Exception:
            pass

    # Клэмпим количество и применяем
    if new_quantity < 1:
        db.remove_from_cart(user_id, product_id)
    else:
        if new_quantity > int(max_stock):
            new_quantity = int(max_stock)
        db.set_cart_quantity(user_id, product_id, new_quantity)

    return {"success": True, "message": "Корзина обновлена", "quantity": new_quantity, "max_stock": int(max_stock)}

@app.post("/api/remove-from-cart")
async def remove_from_cart(data: dict):
    """Удаление товара из корзины"""
    try:
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        
        print(f"🔍 Удаление из корзины: user_id={user_id}, product_id={product_id}")
        print(f"🔍 Типы данных: user_id={type(user_id)}, product_id={type(product_id)}")
        
        if not user_id or not product_id:
            raise HTTPException(status_code=400, detail="User ID and Product ID required")
        
        # Удаляем товар из корзины (product_id может содержать вариант)
        print(f"🗑️ Вызываем db.remove_from_cart с user_id={user_id}, product_id={product_id}")
        db.remove_from_cart(user_id, product_id)
        
        print(f"✅ Товар успешно удален из корзины")
        return {"success": True, "message": "Товар удален из корзины"}
        
    except Exception as e:
        print(f"❌ Ошибка удаления из корзины: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-cart-quantity")
async def update_cart_quantity(data: dict):
    """Обновление количества товара в корзине"""
    try:
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        print(f"🔍 Обновление количества: user_id={user_id}, product_id={product_id}, quantity={quantity}")
        
        if not user_id or not product_id or quantity is None:
            raise HTTPException(status_code=400, detail="User ID, Product ID and Quantity required")
        
        if quantity <= 0:
            # Если количество 0 или меньше, удаляем товар из корзины
            print(f"🗑️ Количество <= 0, удаляем товар из корзины")
            db.remove_from_cart(user_id, product_id)
            return {"success": True, "message": "Товар удален из корзины"}
        
        # Проверяем, не превышает ли количество доступные остатки
        try:
            # Получаем информацию о товаре для проверки остатков
            products = await moysklad.get_products(limit=1000, offset=0)
            base_product_id = product_id.split('_')[0] if '_' in product_id else product_id
            
            product = next((p for p in products if p.get('original_id') == base_product_id), None)
            if product and '_' in product_id:
                parts = product_id.split('_')
                if len(parts) >= 3:  # original_id_color_size
                    variant_color = parts[1]
                    variant_size = parts[2]
                    
                    # Ищем конкретный вариант
                    variant_stock = 0
                    for variant in product.get('variants', []):
                        if (variant_color in variant.get('colors', []) and 
                            variant_size in variant.get('sizes', [])):
                            variant_stock = variant.get('stock', 0)
                            break
                    
                    if quantity > variant_stock:
                        raise HTTPException(status_code=400, detail=f"Недостаточно товара. Доступно: {variant_stock}")
                    
                    print(f"✅ Проверка остатков: variant stock {variant_stock}, requested {quantity}")
        except Exception as e:
            print(f"⚠️ Предупреждение при проверке остатков: {e}")
            # Продолжаем выполнение, если не удалось проверить остатки
        
        # Обновляем количество в корзине
        print(f"🔄 Обновляем количество в корзине на {quantity}")
        db.set_cart_quantity(user_id, product_id, quantity)
        
        return {"success": True, "message": "Количество обновлено", "quantity": quantity}
        
    except Exception as e:
        print(f"❌ Ошибка обновления количества в корзине: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refresh-products")
async def refresh_products():
    """API для принудительного обновления кэша товаров"""
    try:
        moysklad.force_refresh_products()
        return {"success": True, "message": "Кэш товаров помечен для обновления", "status": "success"}
    except Exception as e:
        print(f"❌ Ошибка обновления кэша товаров: {e}")
        return {"success": False, "message": f"Ошибка обновления кэша товаров: {e}"}

@app.get("/api/product/{product_id}")
async def get_product(product_id: str):
    """Получение товара по ID"""
    try:
        print(f"🔍 Получение товара: product_id={product_id}")
        
        # Получаем все товары и ищем нужный по оригинальному ID
        products = await moysklad.get_products(limit=1000, offset=0)
        
        # Ищем товар по оригинальному ID
        # product_id может быть в формате "original_id" или "original_id_size"
        base_product_id = product_id.split('_')[0] if '_' in product_id else product_id
        print(f"🔍 Ищем товар с base_product_id={base_product_id}")
        
        product = None
        for p in products:
            if p.get('original_id') == base_product_id:
                product = p
                break
        
        if product:
            # Если product_id содержит информацию о варианте (цвет/размер), 
            # вычисляем правильный остаток для этого варианта
            if '_' in product_id:
                parts = product_id.split('_')
                if len(parts) >= 3:  # original_id_color_size
                    variant_color = parts[1]
                    variant_size = parts[2]
                    
                    # Ищем конкретный вариант
                    variant_stock = 0
                    for variant in product.get('variants', []):
                        if (variant_color in variant.get('colors', []) and 
                            variant_size in variant.get('sizes', [])):
                            variant_stock = variant.get('stock', 0)
                            break
                    
                    # Создаем копию продукта с правильным остатком для варианта
                    product_copy = product.copy()
                    product_copy['stock'] = variant_stock
                    print(f"✅ Товар найден: {product_copy.get('name', 'Unknown')}, variant stock: {variant_stock} (color: {variant_color}, size: {variant_size})")
                    return {"product": product_copy}
            
            print(f"✅ Товар найден: {product.get('name', 'Unknown')}, stock: {product.get('stock', 0)}")
            return {"product": product}
        else:
            print(f"❌ Товар не найден с ID: {base_product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        print(f"Ошибка получения товара: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/product/{product_id}")
async def product_page(product_id: str):
    """Страница товара"""
    try:
        # Получаем больше товаров для поиска
        products = await moysklad.get_products(limit=1000, offset=0)
        
        # Ищем товар
        product = None
        for p in products:
            if p.get('original_id') == product_id:
                product = p
                break
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return templates.TemplateResponse("product.html", {
            "request": {}, 
            "product": product
        })
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Получение статистики кэша изображений"""
    return {"message": "Image cache not implemented"}

@app.post("/api/cache/clear")
async def clear_cache():
    """Очистка устаревших записей кэша"""
    return {"message": "Image cache not implemented"}

@app.get("/proxy/image/{image_id}")
async def proxy_image(image_id: str):
    """Прокси для изображений MoySklad с авторизацией"""
    try:
        # Получаем заголовки авторизации из MoySklad
        headers = moysklad.headers
        
        # Формируем URL изображения
        image_url = f"https://api.moysklad.ru/api/remap/1.2/download/{image_id}"
        
        # Загружаем изображение с авторизацией
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, headers=headers) as response:
                if response.status == 200:
                    # Получаем содержимое изображения
                    image_data = await response.read()
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    
                    # Возвращаем изображение
                    return Response(
                        content=image_data,
                        media_type=content_type,
                        headers={
                            'Cache-Control': 'public, max-age=3600',
                            'Access-Control-Allow-Origin': '*'
                        }
                    )
                else:
                    raise HTTPException(status_code=response.status, detail="Image not found")
                    
    except Exception as e:
        print(f"❌ Ошибка прокси изображения: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading image: {e}")

if __name__ == "__main__":
    uvicorn.run("webapp:app", host="0.0.0.0", port=8000, reload=True)

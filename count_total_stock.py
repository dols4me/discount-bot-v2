import aiohttp
import asyncio
import json

async def count_total_stock():
    print("🔍 Подсчитываем общее количество stock всех товаров...")
    
    # Получаем все товары через API
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/products?limit=1000") as response:
            if response.status == 200:
                data = await response.json()
                products = data.get('products', [])
                
                print(f"📦 Получено товаров: {len(products)}")
                
                # Подсчитываем общий stock
                total_stock = 0
                positive_stock = 0
                zero_stock = 0
                negative_stock = 0
                
                stock_by_category = {}
                
                for product in products:
                    stock = product.get('stock', 0)
                    category = product.get('category', 'unknown')
                    
                    total_stock += stock
                    
                    if stock > 0:
                        positive_stock += stock
                    elif stock == 0:
                        zero_stock += 1
                    else:
                        negative_stock += stock
                    
                    # Группируем по категориям
                    if category not in stock_by_category:
                        stock_by_category[category] = 0
                    stock_by_category[category] += stock
                
                print(f"\n📊 ОБЩАЯ СТАТИСТИКА STOCK:")
                print(f"📦 Общий stock всех товаров: {total_stock}")
                print(f"✅ Товары с положительным stock: {positive_stock}")
                print(f"⚠️ Товары с нулевым stock: {zero_stock}")
                print(f"❌ Товары с отрицательным stock: {negative_stock}")
                
                print(f"\n🏷️ STOCK ПО КАТЕГОРИЯМ:")
                # Сортируем по убыванию stock
                sorted_categories = sorted(stock_by_category.items(), key=lambda x: x[1], reverse=True)
                
                for category, stock in sorted_categories:
                    if stock != 0:  # Показываем только категории с ненулевым stock
                        print(f"  {category}: {stock}")
                
                print(f"\n📈 ДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА:")
                print(f"📊 Средний stock на товар: {total_stock / len(products):.2f}")
                print(f"📊 Товаров с stock > 0: {sum(1 for p in products if p.get('stock', 0) > 0)}")
                print(f"📊 Товаров с stock = 0: {sum(1 for p in products if p.get('stock', 0) == 0)}")
                print(f"📊 Товаров с stock < 0: {sum(1 for p in products if p.get('stock', 0) < 0)}")
                
            else:
                print(f"❌ Ошибка получения товаров: {response.status}")

if __name__ == "__main__":
    asyncio.run(count_total_stock())

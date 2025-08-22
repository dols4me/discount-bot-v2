import aiohttp
import asyncio
import json

async def test_variants_api():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # 1. Получаем товары (products)
    print("🔍 Получаем товары (products)...")
    products_url = f"{base_url}/entity/product"
    products_params = {'limit': 5}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(products_url, headers=headers, params=products_params) as response:
            if response.status == 200:
                products_data = await response.json()
                print(f"📦 Получено товаров: {len(products_data.get('rows', []))}")
                
                if products_data.get('rows'):
                    for i, product in enumerate(products_data['rows'][:3]):
                        print(f"\n🔍 Товар {i+1}:")
                        print(f"📄 ID: {product.get('id')}")
                        print(f"📄 Название: {product.get('name')}")
                        print(f"📄 Артикул: {product.get('article')}")
                        print(f"📁 Категория: {product.get('productFolder', {}).get('name', 'Нет категории')}")
                        
                        # Проверяем, есть ли модификации у этого товара
                        if product.get('variantsCount', 0) > 0:
                            print(f"🔄 Есть модификации: {product.get('variantsCount')}")
                        else:
                            print("🔄 Нет модификаций")
            else:
                print(f"❌ Ошибка получения товаров: {response.status}")
    
    # 2. Получаем модификации (variants)
    print("\n\n🔍 Получаем модификации (variants)...")
    variants_url = f"{base_url}/entity/variant"
    variants_params = {'limit': 5}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(variants_url, headers=headers, params=variants_params) as response:
            if response.status == 200:
                variants_data = await response.json()
                print(f"📦 Получено модификаций: {len(variants_data.get('rows', []))}")
                
                if variants_data.get('rows'):
                    for i, variant in enumerate(variants_data['rows'][:3]):
                        print(f"\n🔍 Модификация {i+1}:")
                        print(f"📄 ID: {variant.get('id')}")
                        print(f"📄 Название: {variant.get('name')}")
                        print(f"📄 Артикул: {variant.get('article')}")
                        
                        # Информация о родительском товаре
                        if variant.get('product'):
                            product_info = variant['product']
                            print(f"📄 Родительский товар: {product_info.get('name')}")
                            print(f"📄 ID родительского товара: {product_info.get('id')}")
                        
                        # Характеристики модификации
                        if variant.get('characteristics'):
                            print(f"🔧 Характеристики:")
                            for char in variant['characteristics']:
                                print(f"  - {char.get('name')}: {char.get('value')}")
            else:
                print(f"❌ Ошибка получения модификаций: {response.status}")
    
    # 3. Тестируем конкретную модификацию из примера
    print("\n\n🔍 Тестируем конкретную модификацию...")
    specific_variant_url = f"{base_url}/entity/variant/5e37fde4-7d98-11f0-0a80-0f06003af77f?expand=product.supplier"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(specific_variant_url, headers=headers) as response:
            if response.status == 200:
                variant_data = await response.json()
                print(f"📄 Модификация: {variant_data.get('name')}")
                print(f"📄 ID: {variant_data.get('id')}")
                
                if variant_data.get('product'):
                    product_info = variant_data['product']
                    print(f"📄 Родительский товар: {product_info.get('name')}")
                    print(f"📄 ID родительского товара: {product_info.get('id')}")
                
                if variant_data.get('characteristics'):
                    print(f"🔧 Характеристики:")
                    for char in variant_data['characteristics']:
                        print(f"  - {char.get('name')}: {char.get('value')}")
            else:
                print(f"❌ Ошибка получения модификации: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_variants_api())

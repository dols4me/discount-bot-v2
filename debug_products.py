import aiohttp
import asyncio
import json

async def debug_products():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # 1. Получаем родительские товары
    print("🔍 Получаем родительские товары...")
    products_url = f"{base_url}/entity/product"
    products_params = {'limit': 5}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(products_url, headers=headers, params=products_params) as response:
            if response.status == 200:
                products_data = await response.json()
                products = products_data.get('rows', [])
                print(f"📦 Получено товаров: {len(products)}")
                
                if products:
                    first_product = products[0]
                    print(f"🔍 Первый товар: {first_product.get('name')} (ID: {first_product.get('id')})")
                    
                    # Проверяем, есть ли модификации
                    variants_count = first_product.get('variantsCount', 0)
                    print(f"🔄 Количество модификаций: {variants_count}")
    
    # 2. Получаем модификации
    print("\n🔍 Получаем модификации...")
    variants_url = f"{base_url}/entity/variant"
    variants_params = {
        'limit': 10,
        'expand': 'product.supplier'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(variants_url, headers=headers, params=variants_params) as response:
            if response.status == 200:
                variants_data = await response.json()
                variants = variants_data.get('rows', [])
                print(f"📦 Получено модификаций: {len(variants)}")
                
                if variants:
                    print("\n🔍 Первые 3 модификации:")
                    for i, variant in enumerate(variants[:3]):
                        print(f"\nМодификация {i+1}:")
                        print(f"📄 ID: {variant.get('id')}")
                        print(f"📄 Название: {variant.get('name')}")
                        
                        # Проверяем связь с родительским товаром
                        if variant.get('product'):
                            product_info = variant['product']
                            print(f"📄 Родительский товар: {product_info.get('name')}")
                            print(f"📄 ID родительского товара: {product_info.get('id')}")
                        else:
                            print("📄 Родительский товар: НЕТ СВЯЗИ")
                        
                        # Проверяем характеристики
                        if variant.get('characteristics'):
                            print(f"🔧 Характеристики:")
                            for char in variant['characteristics']:
                                print(f"  - {char.get('name')}: {char.get('value')}")
                        else:
                            print("🔧 Характеристики: НЕТ")
    
    # 3. Группируем модификации по товарам
    print("\n🔍 Группируем модификации по товарам...")
    variants_by_product = {}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(variants_url, headers=headers, params=variants_params) as response:
            if response.status == 200:
                variants_data = await response.json()
                variants = variants_data.get('rows', [])
                
                for variant in variants:
                    if variant.get('product') and variant['product'].get('id'):
                        product_id = variant['product']['id']
                        if product_id not in variants_by_product:
                            variants_by_product[product_id] = []
                        variants_by_product[product_id].append(variant)
                
                print(f"📋 Сгруппировано модификаций по товарам: {len(variants_by_product)}")
                
                # Показываем первые несколько групп
                for i, (product_id, product_variants) in enumerate(list(variants_by_product.items())[:3]):
                    print(f"\nГруппа {i+1}:")
                    print(f"📄 ID товара: {product_id}")
                    print(f"📄 Количество модификаций: {len(product_variants)}")
                    
                    for j, variant in enumerate(product_variants[:2]):
                        print(f"  Модификация {j+1}: {variant.get('name')}")

if __name__ == "__main__":
    asyncio.run(debug_products())

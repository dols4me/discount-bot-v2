import aiohttp
import asyncio
import json

async def debug_full_products():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # 1. Получаем все родительские товары
    print("🔍 Получаем все родительские товары...")
    products_url = f"{base_url}/entity/product"
    products_params = {'limit': 2000}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(products_url, headers=headers, params=products_params) as response:
            if response.status == 200:
                products_data = await response.json()
                products = products_data.get('rows', [])
                print(f"📦 Получено товаров: {len(products)}")
                
                # Подсчитываем товары с модификациями
                products_with_variants = 0
                total_variants = 0
                
                for product in products:
                    variants_count = product.get('variantsCount', 0)
                    if variants_count > 0:
                        products_with_variants += 1
                        total_variants += variants_count
                
                print(f"📊 Товаров с модификациями: {products_with_variants}")
                print(f"📊 Общее количество модификаций: {total_variants}")
                
                # Показываем первые 5 товаров с модификациями
                print("\n🔍 Первые 5 товаров с модификациями:")
                count = 0
                for product in products:
                    if count >= 5:
                        break
                    variants_count = product.get('variantsCount', 0)
                    if variants_count > 0:
                        print(f"📄 {product.get('name')} - {variants_count} модификаций")
                        count += 1
    
    # 2. Получаем все модификации
    print("\n🔍 Получаем все модификации...")
    variants_url = f"{base_url}/entity/variant"
    variants_params = {
        'limit': 2000,
        'expand': 'product.supplier'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(variants_url, headers=headers, params=variants_params) as response:
            if response.status == 200:
                variants_data = await response.json()
                variants = variants_data.get('rows', [])
                print(f"📦 Получено модификаций: {len(variants)}")
                
                # Группируем модификации по товарам
                variants_by_product = {}
                for variant in variants:
                    if variant.get('product') and variant['product'].get('id'):
                        product_id = variant['product']['id']
                        if product_id not in variants_by_product:
                            variants_by_product[product_id] = []
                        variants_by_product[product_id].append(variant)
                
                print(f"📊 Товаров с модификациями (из модификаций): {len(variants_by_product)}")
                
                # Показываем первые 5 групп
                print("\n🔍 Первые 5 групп модификаций:")
                count = 0
                for product_id, product_variants in variants_by_product.items():
                    if count >= 5:
                        break
                    print(f"📄 Товар ID: {product_id}")
                    print(f"  Количество модификаций: {len(product_variants)}")
                    for variant in product_variants[:3]:  # Показываем первые 3 модификации
                        print(f"  - {variant.get('name')}")
                    count += 1

if __name__ == "__main__":
    asyncio.run(debug_full_products())

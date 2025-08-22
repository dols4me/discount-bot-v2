import aiohttp
import asyncio
import json

async def debug_variants_no_product():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # Получаем модификации без expand
    print("🔍 Получаем модификации без expand...")
    variants_url = f"{base_url}/entity/variant"
    variants_params = {'limit': 10}
    
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
                        print(f"📄 Родительский товар: {variant.get('product')}")
                        
                        # Проверяем характеристики
                        if variant.get('characteristics'):
                            print(f"🔧 Характеристики:")
                            for char in variant['characteristics']:
                                print(f"  - {char.get('name')}: {char.get('value')}")
                        else:
                            print("🔧 Характеристики: НЕТ")
    
    # Получаем модификации с expand
    print("\n🔍 Получаем модификации с expand...")
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
                    print("\n🔍 Первые 3 модификации с expand:")
                    for i, variant in enumerate(variants[:3]):
                        print(f"\nМодификация {i+1}:")
                        print(f"📄 ID: {variant.get('id')}")
                        print(f"📄 Название: {variant.get('name')}")
                        
                        if variant.get('product'):
                            product_info = variant['product']
                            print(f"📄 Родительский товар: {product_info.get('name')}")
                            print(f"📄 ID родительского товара: {product_info.get('id')}")
                        else:
                            print("📄 Родительский товар: НЕТ")
                        
                        # Проверяем характеристики
                        if variant.get('characteristics'):
                            print(f"🔧 Характеристики:")
                            for char in variant['characteristics']:
                                print(f"  - {char.get('name')}: {char.get('value')}")
                        else:
                            print("🔧 Характеристики: НЕТ")

if __name__ == "__main__":
    asyncio.run(debug_variants_no_product())

import aiohttp
import asyncio
import json

async def debug_product_structure():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # Получаем первые 3 товара и анализируем их структуру
    print("🔍 Анализируем структуру товаров...")
    products_url = f"{base_url}/entity/product"
    products_params = {'limit': 3}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(products_url, headers=headers, params=products_params) as response:
            if response.status == 200:
                products_data = await response.json()
                products = products_data.get('rows', [])
                
                for i, product in enumerate(products):
                    print(f"\n🔍 Товар {i+1}: {product.get('name')}")
                    print(f"📄 ID: {product.get('id')}")
                    
                    # Проверяем все возможные поля, связанные с категориями
                    print("📋 Анализ полей категории:")
                    
                    # productFolder
                    if product.get('productFolder'):
                        folder = product['productFolder']
                        print(f"  productFolder: {folder}")
                    else:
                        print("  productFolder: НЕТ")
                    
                    # pathName
                    if product.get('pathName'):
                        print(f"  pathName: {product['pathName']}")
                    else:
                        print("  pathName: НЕТ")
                    
                    # folder
                    if product.get('folder'):
                        print(f"  folder: {product['folder']}")
                    else:
                        print("  folder: НЕТ")
                    
                    # category
                    if product.get('category'):
                        print(f"  category: {product['category']}")
                    else:
                        print("  category: НЕТ")
                    
                    # Проверяем все ключи товара
                    print("🔍 Все ключи товара:")
                    for key in product.keys():
                        print(f"  {key}: {product[key]}")
                    
                    print("-" * 50)
            else:
                print(f"❌ Ошибка получения товаров: {response.status}")

if __name__ == "__main__":
    asyncio.run(debug_product_structure())

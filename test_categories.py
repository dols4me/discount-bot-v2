import aiohttp
import asyncio
import json

async def test_categories():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # Получаем категории
    print("🔍 Получаем категории...")
    categories_url = f"{base_url}/entity/productfolder"
    categories_params = {'limit': 1000}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(categories_url, headers=headers, params=categories_params) as response:
            if response.status == 200:
                categories_data = await response.json()
                categories = categories_data.get('rows', [])
                print(f"📦 Получено категорий: {len(categories)}")
                
                print("\n🔍 Все категории:")
                for i, category in enumerate(categories):
                    print(f"{i+1}. {category.get('name')} (ID: {category.get('id')})")
                
                # Проверяем первые 5 товаров и их категории
                print("\n🔍 Проверяем товары и их категории...")
                products_url = f"{base_url}/entity/product"
                products_params = {'limit': 5}
                
                async with session.get(products_url, headers=headers, params=products_params) as response:
                    if response.status == 200:
                        products_data = await response.json()
                        products = products_data.get('rows', [])
                        
                        for i, product in enumerate(products):
                            print(f"\nТовар {i+1}: {product.get('name')}")
                            if product.get('productFolder'):
                                folder = product['productFolder']
                                print(f"  Категория: {folder.get('name')} (ID: {folder.get('id')})")
                            else:
                                print("  Категория: НЕТ")
            else:
                print(f"❌ Ошибка получения категорий: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_categories())

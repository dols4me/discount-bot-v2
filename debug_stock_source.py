import aiohttp
import asyncio
import json

async def debug_stock_source():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    print("🔍 Анализируем источник данных stock из API МойСклад...")
    
    # Получаем остатки товаров
    print("\n📊 Получаем остатки товаров...")
    stock_url = f"{base_url}/report/stock/bystore"
    stock_params = {'limit': 5}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(stock_url, headers=headers, params=stock_params) as response:
            if response.status == 200:
                stock_data = await response.json()
                stock_items = stock_data.get('rows', [])
                
                print(f"📦 Получено остатков: {len(stock_items)}")
                
                for i, stock_item in enumerate(stock_items):
                    print(f"\n🔍 Остаток {i+1}:")
                    print(f"📄 Meta href: {stock_item.get('meta', {}).get('href', 'N/A')}")
                    
                    # Извлекаем ID товара из href
                    meta_href = stock_item.get('meta', {}).get('href', '')
                    if meta_href:
                        item_id = meta_href.split('/')[-1].split('?')[0]
                        print(f"📄 ID товара: {item_id}")
                    
                    # Анализируем stockByStore
                    stock_by_store = stock_item.get('stockByStore', [])
                    print(f"🏪 Количество складов: {len(stock_by_store)}")
                    
                    total_stock = 0
                    for store_stock in stock_by_store:
                        store_name = store_stock.get('name', 'Unknown')
                        stock_value = store_stock.get('stock', 0)
                        total_stock += stock_value
                        print(f"  Склад '{store_name}': {stock_value}")
                    
                    print(f"📊 Общий stock: {total_stock}")
                    print("-" * 50)
            else:
                print(f"❌ Ошибка получения остатков: {response.status}")
    
    # Получаем модификации с остатками
    print("\n🔄 Получаем модификации с остатками...")
    variants_url = f"{base_url}/entity/variant"
    variants_params = {'limit': 5, 'expand': 'product'}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(variants_url, headers=headers, params=variants_params) as response:
            if response.status == 200:
                variants_data = await response.json()
                variants = variants_data.get('rows', [])
                
                print(f"📦 Получено модификаций: {len(variants)}")
                
                for i, variant in enumerate(variants):
                    print(f"\n🔍 Модификация {i+1}:")
                    print(f"📄 ID: {variant.get('id')}")
                    print(f"📄 Название: {variant.get('name')}")
                    
                    # Проверяем, есть ли информация о родительском товаре
                    if variant.get('product'):
                        product = variant['product']
                        print(f"📄 Родительский товар: {product.get('name')} (ID: {product.get('id')})")
                    
                    print("-" * 50)
            else:
                print(f"❌ Ошибка получения модификаций: {response.status}")

if __name__ == "__main__":
    asyncio.run(debug_stock_source())

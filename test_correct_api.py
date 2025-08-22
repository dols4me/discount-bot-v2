import aiohttp
import asyncio
import json

async def test_correct_api():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # 1. Тестируем получение товаров
    print("🔍 Тестируем получение товаров (/entity/product)...")
    url = f"{base_url}/entity/product"
    params = {'limit': 3}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"📦 Получено товаров: {len(data.get('rows', []))}")
                
                if data.get('rows'):
                    for i, product in enumerate(data['rows'][:2]):
                        print(f"🔍 Товар {i+1}: {product.get('name', 'Unknown')}")
                        print(f"📄 ID: {product.get('id')}")
                        print(f"📁 Папка: {product.get('productFolder', {}).get('name', 'Нет папки')}")
                        print(f"💰 Цена: {product.get('salePrices', [{}])[0].get('value', 0) if product.get('salePrices') else 0}")
                        print("---")
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")
    
    # 2. Тестируем получение остатков
    print("\n🔍 Тестируем получение остатков (/entity/stock)...")
    url = f"{base_url}/entity/stock"
    params = {'limit': 5}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"📊 Получено остатков: {len(data.get('rows', []))}")
                
                if data.get('rows'):
                    for i, stock in enumerate(data['rows'][:2]):
                        print(f"🔍 Остаток {i+1}:")
                        print(f"📄 Товар: {stock.get('assortment', {}).get('name', 'Unknown')}")
                        print(f"📦 Количество: {stock.get('quantity', 0)}")
                        print(f"🏪 Склад: {stock.get('store', {}).get('name', 'Unknown')}")
                        print("---")
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")
    
    # 3. Тестируем получение остатков для конкретного товара
    print("\n🔍 Тестируем получение остатков для конкретного товара...")
    # Сначала получаем ID товара
    product_url = f"{base_url}/entity/product"
    product_params = {'limit': 1}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(product_url, headers=headers, params=product_params) as response:
            if response.status == 200:
                product_data = await response.json()
                if product_data.get('rows'):
                    product = product_data['rows'][0]
                    product_id = product.get('id')
                    product_name = product.get('name', 'Unknown')
                    
                    print(f"🔍 Тестируем остатки для товара: {product_name} (ID: {product_id})")
                    
                    # Теперь получаем остатки для этого товара
                    stock_url = f"{base_url}/entity/stock"
                    stock_params = {
                        'filter': f'assortment.id={product_id}',
                        'limit': 5
                    }
                    
                    async with session.get(stock_url, headers=headers, params=stock_params) as stock_response:
                        print(f"📊 Статус ответа остатков: {stock_response.status}")
                        
                        if stock_response.status == 200:
                            stock_data = await stock_response.json()
                            print(f"📊 Получено остатков для товара: {len(stock_data.get('rows', []))}")
                            
                            if stock_data.get('rows'):
                                for stock in stock_data['rows']:
                                    print(f"📦 Остаток: {stock.get('quantity', 0)} на складе {stock.get('store', {}).get('name', 'Unknown')}")
                            else:
                                print("📦 Остатков не найдено")
                        else:
                            error_text = await stock_response.text()
                            print(f"❌ Ошибка получения остатков: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_correct_api())

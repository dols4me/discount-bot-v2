import aiohttp
import asyncio
import json

async def test_bystore_api():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # Тестируем получение остатков по складам
    print("🔍 Тестируем получение остатков (/report/stock/bystore)...")
    url = f"{base_url}/report/stock/bystore"
    params = {'limit': 5}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"📦 Получено остатков: {len(data.get('rows', []))}")
                
                if data.get('rows'):
                    for i, stock in enumerate(data['rows'][:3]):
                        print(f"🔍 Остаток {i+1}:")
                        print(f"📄 Товар: {stock.get('name', 'Unknown')}")
                        print(f"📦 Количество: {stock.get('stock', 0)}")
                        print(f"🏪 Склад: {stock.get('store', 'Unknown')}")
                        print(f"💰 Цена: {stock.get('salePrice', 0)}")
                        print(f"📁 Категория: {stock.get('folder', {}).get('name', 'Нет категории')}")
                        print("---")
                else:
                    print("📦 Остатков не найдено")
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")
    
    # Тестируем получение остатков для конкретного склада
    print("\n🔍 Тестируем получение остатков для конкретного склада...")
    
    # Сначала получим список складов
    stores_url = f"{base_url}/entity/store"
    stores_params = {'limit': 2}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(stores_url, headers=headers, params=stores_params) as response:
            if response.status == 200:
                stores_data = await response.json()
                if stores_data.get('rows'):
                    store = stores_data['rows'][0]
                    store_id = store.get('id')
                    store_name = store.get('name', 'Unknown')
                    
                    print(f"🔍 Тестируем остатки для склада: {store_name} (ID: {store_id})")
                    
                    # Теперь получаем остатки для этого склада
                    bystore_url = f"{base_url}/report/stock/bystore"
                    bystore_params = {
                        'store': store_id,
                        'limit': 3
                    }
                    
                    async with session.get(bystore_url, headers=headers, params=bystore_params) as bystore_response:
                        print(f"📊 Статус ответа остатков по складу: {bystore_response.status}")
                        
                        if bystore_response.status == 200:
                            bystore_data = await bystore_response.json()
                            print(f"📊 Получено остатков на складе: {len(bystore_data.get('rows', []))}")
                            
                            if bystore_data.get('rows'):
                                for stock in bystore_data['rows']:
                                    print(f"📦 Товар: {stock.get('name', 'Unknown')} - {stock.get('stock', 0)} шт.")
                            else:
                                print("📦 Остатков на складе не найдено")
                        else:
                            error_text = await bystore_response.text()
                            print(f"❌ Ошибка получения остатков по складу: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_bystore_api())

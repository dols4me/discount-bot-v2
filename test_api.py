import aiohttp
import asyncio
import json

async def test_api():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # Тестируем получение товаров
    print("🔍 Тестируем получение товаров...")
    url = f"{base_url}/entity/product"
    params = {'limit': 1}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"📦 Получено товаров: {len(data.get('rows', []))}")
                
                if data.get('rows'):
                    product = data['rows'][0]
                    print(f"🔍 Первый товар:")
                    print(json.dumps(product, indent=2, ensure_ascii=False))
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")
    
    # Тестируем получение остатков (новый API)
    print("\n🔍 Тестируем получение остатков (bystore/current)...")
    url = f"{base_url}/report/stock/bystore/current"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"📦 Получено остатков: {len(data) if isinstance(data, list) else len(data.get('rows', []))}")
                
                if isinstance(data, list) and data:
                    stock_item = data[0]
                    print(f"🔍 Первый остаток:")
                    print(json.dumps(stock_item, indent=2, ensure_ascii=False))
                elif data.get('rows') and data['rows']:
                    stock_item = data['rows'][0]
                    print(f"🔍 Первый остаток:")
                    print(json.dumps(stock_item, indent=2, ensure_ascii=False))
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")
    
    # Тестируем старый API остатков
    print("\n🔍 Тестируем старый API остатков (/report/stock/all)...")
    url = f"{base_url}/report/stock/all"
    params = {'limit': 1}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"📦 Получено остатков: {len(data.get('rows', []))}")
                
                if data.get('rows'):
                    stock_item = data['rows'][0]
                    print(f"🔍 Первый остаток:")
                    print(json.dumps(stock_item, indent=2, ensure_ascii=False))
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_api())

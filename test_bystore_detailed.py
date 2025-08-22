import aiohttp
import asyncio
import json

async def test_bystore_detailed():
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
    params = {'limit': 3}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"📦 Получено остатков: {len(data.get('rows', []))}")
                print(f"📄 Структура ответа: {list(data.keys())}")
                
                if data.get('rows'):
                    for i, stock in enumerate(data['rows']):
                        print(f"\n🔍 Остаток {i+1}:")
                        print(f"📄 Все поля: {list(stock.keys())}")
                        print(f"📄 Полные данные: {json.dumps(stock, indent=2, ensure_ascii=False)}")
                        print("---")
                else:
                    print("📦 Остатков не найдено")
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_bystore_detailed())

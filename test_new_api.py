import aiohttp
import asyncio
import json
import time

async def test_new_api():
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
    params = {'limit': 2}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"📦 Получено товаров: {len(data.get('rows', []))}")
                
                if data.get('rows'):
                    product = data['rows'][0]
                    print(f"🔍 Первый товар: {product.get('name', 'Unknown')}")
                    print(f"📄 ID товара: {product.get('id')}")
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")
    
    # 2. Тестируем получение модификаций
    print("\n🔍 Тестируем получение модификаций (/entity/product/variants)...")
    url = f"{base_url}/entity/product/variants"
    params = {'limit': 2}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"🔄 Получено модификаций: {len(data.get('rows', []))}")
                
                if data.get('rows'):
                    variant = data['rows'][0]
                    print(f"🔍 Первая модификация: {variant.get('name', 'Unknown')}")
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")
    
    # 3. Тестируем получение остатков
    print("\n🔍 Тестируем получение остатков (/report/stock/byproduct)...")
    url = f"{base_url}/report/stock/byproduct"
    
    request_data = {
        "date": time.strftime("%Y-%m-%d"),
        "useStock": True,
        "useBalance": True
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=request_data) as response:
            print(f"📊 Статус ответа: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"📊 Получено остатков: {len(data.get('rows', []))}")
                
                if data.get('rows'):
                    stock_item = data['rows'][0]
                    print(f"🔍 Первый остаток: {stock_item}")
            else:
                error_text = await response.text()
                print(f"❌ Ошибка: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_new_api())

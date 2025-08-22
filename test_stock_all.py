import aiohttp
import asyncio
import json

async def test_stock_all():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    print("🔍 Тестируем /report/stock/all...")
    
    # Пробуем разные параметры
    test_params = [
        {'limit': 1000},
        {'limit': 2000},
        {'limit': 1000, 'offset': 0},
        {'limit': 1000, 'moment': '2024-12-19 00:00:00'},
        {'limit': 1000, 'store': 'all'}
    ]
    
    for i, params in enumerate(test_params):
        print(f"\n📊 Тест {i+1} с параметрами: {params}")
        
        stock_all_url = f"{base_url}/report/stock/all"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(stock_all_url, headers=headers, params=params) as response:
                if response.status == 200:
                    stock_all_data = await response.json()
                    stock_all_items = stock_all_data.get('rows', [])
                    
                    print(f"📦 Получено товаров: {len(stock_all_items)}")
                    
                    # Подсчитываем общий stock
                    total_stock = 0
                    positive_stock = 0
                    zero_stock = 0
                    negative_stock = 0
                    
                    for item in stock_all_items:
                        # Пробуем разные поля
                        stock = item.get('quantity', 0)  # Основное поле
                        if stock == 0:
                            stock = item.get('stock', 0)  # Альтернативное поле
                        
                        total_stock += stock
                        
                        if stock > 0:
                            positive_stock += stock
                        elif stock == 0:
                            zero_stock += 1
                        else:
                            negative_stock += stock
                    
                    print(f"📊 Общий stock: {total_stock}")
                    print(f"✅ Положительный stock: {positive_stock}")
                    print(f"⚠️ Товары с нулевым stock: {zero_stock}")
                    print(f"❌ Отрицательный stock: {negative_stock}")
                    
                    if total_stock == 896:
                        print(f"🎉 НАЙДЕНО! Правильное значение 896 с параметрами {params}")
                        break
                    
                else:
                    print(f"❌ Ошибка: {response.status}")
    
    # Также проверим структуру данных
    print(f"\n🔍 Анализируем структуру данных...")
    stock_all_url = f"{base_url}/report/stock/all"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(stock_all_url, headers=headers, params={'limit': 5}) as response:
            if response.status == 200:
                stock_all_data = await response.json()
                stock_all_items = stock_all_data.get('rows', [])
                
                if stock_all_items:
                    print(f"📄 Структура первого товара:")
                    first_item = stock_all_items[0]
                    for key, value in first_item.items():
                        print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_stock_all())

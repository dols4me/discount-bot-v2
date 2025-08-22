import aiohttp
import asyncio
import json

async def compare_stock_sources():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    print("🔍 Сравниваем источники данных stock...")
    
    # 1. Получаем данные из /report/stock/all
    print("\n📊 Получаем данные из /report/stock/all...")
    stock_all_url = f"{base_url}/report/stock/all"
    stock_all_params = {'limit': 1000}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(stock_all_url, headers=headers, params=stock_all_params) as response:
            if response.status == 200:
                stock_all_data = await response.json()
                stock_all_items = stock_all_data.get('rows', [])
                
                print(f"📦 Получено товаров из /report/stock/all: {len(stock_all_items)}")
                
                # Подсчитываем общий stock
                total_stock_all = 0
                positive_stock_all = 0
                zero_stock_all = 0
                negative_stock_all = 0
                
                for item in stock_all_items:
                    stock = item.get('quantity', 0)
                    total_stock_all += stock
                    
                    if stock > 0:
                        positive_stock_all += stock
                    elif stock == 0:
                        zero_stock_all += 1
                    else:
                        negative_stock_all += stock
                
                print(f"📊 Общий stock из /report/stock/all: {total_stock_all}")
                print(f"✅ Положительный stock: {positive_stock_all}")
                print(f"⚠️ Товары с нулевым stock: {zero_stock_all}")
                print(f"❌ Отрицательный stock: {negative_stock_all}")
                
                # Показываем первые 5 товаров
                print(f"\n🔍 Первые 5 товаров из /report/stock/all:")
                for i, item in enumerate(stock_all_items[:5]):
                    print(f"  {i+1}. {item.get('name', 'Unknown')} - Stock: {item.get('quantity', 0)}")
                
            else:
                print(f"❌ Ошибка получения /report/stock/all: {response.status}")
    
    # 2. Получаем данные из /report/stock/bystore
    print("\n📊 Получаем данные из /report/stock/bystore...")
    stock_bystore_url = f"{base_url}/report/stock/bystore"
    stock_bystore_params = {'limit': 1000}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(stock_bystore_url, headers=headers, params=stock_bystore_params) as response:
            if response.status == 200:
                stock_bystore_data = await response.json()
                stock_bystore_items = stock_bystore_data.get('rows', [])
                
                print(f"📦 Получено товаров из /report/stock/bystore: {len(stock_bystore_items)}")
                
                # Подсчитываем общий stock
                total_stock_bystore = 0
                positive_stock_bystore = 0
                zero_stock_bystore = 0
                negative_stock_bystore = 0
                
                for item in stock_bystore_items:
                    # Считаем общий stock по всем складам
                    total_stock = 0
                    for store_stock in item.get('stockByStore', []):
                        total_stock += store_stock.get('stock', 0)
                    
                    total_stock_bystore += total_stock
                    
                    if total_stock > 0:
                        positive_stock_bystore += total_stock
                    elif total_stock == 0:
                        zero_stock_bystore += 1
                    else:
                        negative_stock_bystore += total_stock
                
                print(f"📊 Общий stock из /report/stock/bystore: {total_stock_bystore}")
                print(f"✅ Положительный stock: {positive_stock_bystore}")
                print(f"⚠️ Товары с нулевым stock: {zero_stock_bystore}")
                print(f"❌ Отрицательный stock: {negative_stock_bystore}")
                
                # Показываем первые 5 товаров
                print(f"\n🔍 Первые 5 товаров из /report/stock/bystore:")
                for i, item in enumerate(stock_bystore_items[:5]):
                    meta_href = item.get('meta', {}).get('href', '')
                    total_stock = sum(store.get('stock', 0) for store in item.get('stockByStore', []))
                    print(f"  {i+1}. {meta_href} - Stock: {total_stock}")
                
            else:
                print(f"❌ Ошибка получения /report/stock/bystore: {response.status}")
    
    # 3. Сравнение
    print(f"\n📊 СРАВНЕНИЕ:")
    print(f"📦 /report/stock/all: {total_stock_all}")
    print(f"📦 /report/stock/bystore: {total_stock_bystore}")
    print(f"📦 Разница: {total_stock_all - total_stock_bystore}")
    
    if total_stock_all == 896:
        print(f"✅ /report/stock/all показывает 896 единиц - это правильное значение!")
    else:
        print(f"❌ /report/stock/all показывает {total_stock_all}, а должно быть 896")

if __name__ == "__main__":
    asyncio.run(compare_stock_sources())

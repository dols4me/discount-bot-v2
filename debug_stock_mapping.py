import aiohttp
import asyncio
import json

async def debug_stock_mapping():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    print("🔍 Отлаживаем сопоставление данных stock...")
    
    # Получаем данные из /report/stock/all
    print("\n📊 Получаем данные из /report/stock/all...")
    stock_all_url = f"{base_url}/report/stock/all"
    stock_all_params = {'limit': 1000}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(stock_all_url, headers=headers, params=stock_all_params) as response:
            if response.status == 200:
                stock_all_data = await response.json()
                stock_all_items = stock_all_data.get('rows', [])
                
                print(f"📦 Получено товаров из /report/stock/all: {len(stock_all_items)}")
                
                # Создаем словарь остатков
                stock_dict = {}
                total_positive_stock = 0
                
                for item in stock_all_items:
                    meta_href = item.get('meta', {}).get('href', '')
                    if meta_href:
                        item_id = meta_href.split('/')[-1].split('?')[0]
                        quantity = item.get('quantity', 0)
                        stock_dict[item_id] = quantity
                        
                        if quantity > 0:
                            total_positive_stock += quantity
                
                print(f"📊 Создан словарь остатков: {len(stock_dict)} позиций")
                print(f"📊 Общий положительный stock: {total_positive_stock}")
                
                # Получаем товары через наш API
                print("\n📊 Получаем данные через наш API...")
                async with session.get("http://localhost:8000/api/products?limit=10") as response:
                    if response.status == 200:
                        data = await response.json()
                        products = data.get('products', [])
                        
                        print(f"📦 Получено товаров через API: {len(products)}")
                        
                        total_api_stock = 0
                        for product in products:
                            product_id = product.get('original_id')
                            api_stock = product.get('stock', 0)
                            direct_stock = stock_dict.get(product_id, 0)
                            
                            total_api_stock += api_stock
                            
                            if api_stock != direct_stock:
                                print(f"⚠️ Несоответствие для {product.get('name')}:")
                                print(f"  API stock: {api_stock}")
                                print(f"  Direct stock: {direct_stock}")
                                print(f"  Product ID: {product_id}")
                        
                        print(f"\n📊 Сравнение:")
                        print(f"📦 Общий stock через API: {total_api_stock}")
                        print(f"📦 Общий положительный stock из /report/stock/all: {total_positive_stock}")
                        print(f"📦 Разница: {total_positive_stock - total_api_stock}")
                        
                        if total_positive_stock == 896:
                            print(f"✅ /report/stock/all показывает правильное значение 896!")
                        else:
                            print(f"❌ /report/stock/all показывает {total_positive_stock}, а должно быть 896")
                        
            else:
                print(f"❌ Ошибка получения /report/stock/all: {response.status}")

if __name__ == "__main__":
    asyncio.run(debug_stock_mapping())

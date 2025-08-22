import aiohttp
import asyncio
import json

async def test_total_products():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # 1. Проверяем общее количество товаров
    print("🔍 Проверяем общее количество товаров...")
    url = f"{base_url}/entity/product"
    params = {'limit': 1}  # Запрашиваем только 1 товар, чтобы получить meta
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                total_count = data.get('meta', {}).get('size', 0)
                print(f"📊 Общее количество товаров в системе: {total_count}")
                
                # 2. Проверяем количество товаров с остатками
                print("\n🔍 Проверяем количество товаров с остатками...")
                stock_url = f"{base_url}/report/stock/bystore"
                stock_params = {'limit': 1}
                
                async with session.get(stock_url, headers=headers, params=stock_params) as stock_response:
                    if stock_response.status == 200:
                        stock_data = await stock_response.json()
                        stock_total = stock_data.get('meta', {}).get('size', 0)
                        print(f"📊 Товаров с остатками: {stock_total}")
                        
                        # 3. Проверяем количество товаров без остатков
                        without_stock = total_count - stock_total
                        print(f"📊 Товаров без остатков: {without_stock}")
                        
                        print(f"\n📈 Статистика:")
                        print(f"- Всего товаров в системе: {total_count}")
                        print(f"- Товаров с остатками: {stock_total}")
                        print(f"- Товаров без остатков: {without_stock}")
                        
                        if total_count > 0:
                            stock_percentage = (stock_total / total_count) * 100
                            print(f"- Процент товаров с остатками: {stock_percentage:.1f}%")
                    else:
                        print(f"❌ Ошибка получения остатков: {stock_response.status}")
            else:
                print(f"❌ Ошибка получения товаров: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_total_products())

import aiohttp
import asyncio
import json

async def test_variants_expanded():
    api_token = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"
    base_url = "https://api.moysklad.ru/api/remap/1.2"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # Получаем модификации с расширенной информацией
    print("🔍 Получаем модификации с расширенной информацией...")
    variants_url = f"{base_url}/entity/variant"
    variants_params = {
        'limit': 5,
        'expand': 'product.supplier'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(variants_url, headers=headers, params=variants_params) as response:
            if response.status == 200:
                variants_data = await response.json()
                print(f"📦 Получено модификаций: {len(variants_data.get('rows', []))}")
                
                if variants_data.get('rows'):
                    for i, variant in enumerate(variants_data['rows']):
                        print(f"\n🔍 Модификация {i+1}:")
                        print(f"📄 ID: {variant.get('id')}")
                        print(f"📄 Название: {variant.get('name')}")
                        print(f"📄 Артикул: {variant.get('article')}")
                        
                        # Информация о родительском товаре
                        if variant.get('product'):
                            product_info = variant['product']
                            print(f"📄 Родительский товар: {product_info.get('name')}")
                            print(f"📄 ID родительского товара: {product_info.get('id')}")
                            print(f"📄 Артикул родительского товара: {product_info.get('article')}")
                        else:
                            print("📄 Родительский товар: Нет связи")
                        
                        # Характеристики модификации
                        if variant.get('characteristics'):
                            print(f"🔧 Характеристики:")
                            for char in variant['characteristics']:
                                print(f"  - {char.get('name')}: {char.get('value')}")
                        else:
                            print("🔧 Характеристики: Нет")
                        
                        # Цены
                        if variant.get('salePrices'):
                            print(f"💰 Цены:")
                            for price in variant['salePrices']:
                                print(f"  - {price.get('value', 0) / 100} руб.")
            else:
                print(f"❌ Ошибка получения модификаций: {response.status}")
                error_text = await response.text()
                print(f"📄 Текст ошибки: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_variants_expanded())

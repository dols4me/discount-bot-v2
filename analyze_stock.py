import aiohttp
import asyncio
import json

async def analyze_stock():
    print("🔍 Анализируем расчет stock/quantity товаров...")
    
    # Получаем товары через API
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/products?limit=10") as response:
            if response.status == 200:
                data = await response.json()
                products = data.get('products', [])
                
                print(f"📦 Получено товаров для анализа: {len(products)}")
                print("\n" + "="*80)
                
                for i, product in enumerate(products):
                    print(f"\n🔍 Товар {i+1}: {product.get('name')}")
                    print(f"📄 ID: {product.get('original_id')}")
                    print(f"💰 Цена: {product.get('price')}")
                    print(f"📊 Stock (общий): {product.get('stock')}")
                    print(f"📋 Модификации: {product.get('modifications_text')}")
                    
                    # Анализируем варианты
                    variants = product.get('variants', [])
                    print(f"🔧 Количество вариантов: {len(variants)}")
                    
                    total_variant_stock = 0
                    for j, variant in enumerate(variants):
                        variant_stock = variant.get('stock', 0)
                        total_variant_stock += variant_stock
                        print(f"  Вариант {j+1}: {variant.get('name')} - Stock: {variant_stock}")
                    
                    print(f"📊 Сумма stock всех вариантов: {total_variant_stock}")
                    print(f"📊 Stock товара: {product.get('stock')}")
                    
                    if total_variant_stock != product.get('stock'):
                        print("⚠️  ВНИМАНИЕ: Сумма вариантов не равна stock товара!")
                    
                    print("-" * 60)
                
                # Анализируем общую статистику
                print("\n📊 ОБЩАЯ СТАТИСТИКА:")
                total_stock = sum(p.get('stock', 0) for p in products)
                total_variants = sum(len(p.get('variants', [])) for p in products)
                total_variant_stock = sum(sum(v.get('stock', 0) for v in p.get('variants', [])) for p in products)
                
                print(f"📦 Общий stock всех товаров: {total_stock}")
                print(f"🔧 Общее количество вариантов: {total_variants}")
                print(f"📊 Общий stock всех вариантов: {total_variant_stock}")
                
                if total_stock != total_variant_stock:
                    print("⚠️  ВНИМАНИЕ: Общий stock товаров не равен сумме stock вариантов!")
                else:
                    print("✅ Stock товаров равен сумме stock вариантов")
                    
            else:
                print(f"❌ Ошибка получения товаров: {response.status}")

if __name__ == "__main__":
    asyncio.run(analyze_stock())

#!/usr/bin/env python3
import requests
import json

def test_brak_categorization():
    """Тестируем новую логику категоризации в 'Брак'"""
    
    # Получаем товары
    response = requests.get("http://localhost:8000/api/products?limit=50&offset=0")
    if response.status_code != 200:
        print(f"❌ Ошибка API: {response.status_code}")
        return
    
    data = response.json()
    products = data.get('products', [])
    
    print(f"🔍 Тестируем категоризацию первых {len(products)} товаров:\n")
    
    # Группируем по категориям
    categories = {}
    brak_products = []
    
    for product in products:
        category = product.get('category', 'NO CATEGORY')
        name = product.get('name', 'NO NAME')
        
        if category not in categories:
            categories[category] = []
        categories[category].append(name)
        
        if category == 'Брак':
            brak_products.append({
                'name': name,
                'modifications': product.get('modifications_text', 'НЕТ')
            })
    
    print("📊 Распределение по категориям:\n")
    for category, names in categories.items():
        print(f"🏷️  {category}: {len(names)} товаров")
        for name in names[:3]:  # Показываем первые 3 товара
            print(f"   - {name}")
        if len(names) > 3:
            print(f"   ... и еще {len(names) - 3} товаров")
        print()
    
    print("🚨 Товары в категории 'Брак':\n")
    for i, product in enumerate(brak_products, 1):
        print(f"📦 {i}. {product['name']}")
        print(f"   Модификации: {product['modifications']}")
        print()

if __name__ == "__main__":
    try:
        test_brak_categorization()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Убедитесь, что сервер запущен на http://localhost:8000")

import requests
import json

def analyze_products():
    # Получаем все товары
    response = requests.get("http://localhost:8000/api/products?limit=1000")
    data = response.json()
    
    products = data['products']
    print(f"Всего товаров загружено: {len(products)}")
    
    # Анализируем категории
    categories = {}
    for product in products:
        category = product['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(product['name'])
    
    print("\nРаспределение по категориям:")
    for category, items in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{category} ({len(items)} товаров):")
        for i, name in enumerate(items[:5]):  # Показываем первые 5 товаров
            print(f"  {i+1}. {name}")
        if len(items) > 5:
            print(f"  ... и еще {len(items) - 5} товаров")
    
    # Анализируем модификации
    print("\n\nАнализ модификаций:")
    products_with_sizes = [p for p in products if p['available_sizes']]
    products_with_colors = [p for p in products if p['available_colors']]
    products_with_both = [p for p in products if p['available_sizes'] and p['available_colors']]
    
    print(f"Товары с размерами: {len(products_with_sizes)}")
    print(f"Товары с цветами: {len(products_with_colors)}")
    print(f"Товары с размерами и цветами: {len(products_with_both)}")
    
    # Показываем примеры размеров и цветов
    all_sizes = set()
    all_colors = set()
    for product in products:
        all_sizes.update(product['available_sizes'])
        all_colors.update(product['available_colors'])
    
    print(f"\nВсе размеры: {sorted(all_sizes)}")
    print(f"Все цвета: {sorted(all_colors)}")

if __name__ == "__main__":
    analyze_products()

#!/usr/bin/env python3
"""
Скрипт для анализа данных, которые уже загружены в боте
"""

import requests
import json

def analyze_bot_data():
    """Анализирует данные, которые уже загружены в боте"""
    
    print("🔍 Анализируем данные в боте...")
    print("=" * 80)
    
    # Получаем первые 10 товаров из бота
    try:
        response = requests.get("http://localhost:8000/api/products?limit=10&offset=0")
        if response.status_code == 200:
            products = response.json()['products']
        else:
            print(f"❌ Ошибка получения данных: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    
    print(f"📊 Получено товаров: {len(products)}")
    print("\n" + "=" * 80)
    
    # Анализируем каждый товар
    total_variants = 0
    total_colors = 0
    total_sizes = 0
    products_with_variants = 0
    products_without_variants = 0
    
    for i, product in enumerate(products, 1):
        print(f"\n{i}. {product['name']}")
        print(f"   ID: {product['original_id']}")
        print(f"   Категория: {product['category']}")
        print(f"   Общий stock: {product['stock']}")
        
        # Анализируем цвета
        colors = product['available_colors']
        colors_count = len(colors)
        total_colors += colors_count
        if colors_count > 0:
            print(f"   Цвета ({colors_count}): {', '.join(colors)}")
        else:
            print(f"   Цвета: нет")
        
        # Анализируем размеры
        sizes = product['available_sizes']
        sizes_count = len(sizes)
        total_sizes += sizes_count
        if sizes_count > 0:
            print(f"   Размеры ({sizes_count}): {', '.join(sizes)}")
        else:
            print(f"   Размеры: нет")
        
        # Анализируем варианты
        variants = product['variants']
        variants_count = len(variants)
        total_variants += variants_count
        
        if variants_count > 0:
            products_with_variants += 1
            print(f"   Варианты ({variants_count}):")
            for j, variant in enumerate(variants, 1):
                variant_stock = variant.get('stock', 0)
                variant_colors = variant.get('colors', [])
                variant_sizes = variant.get('sizes', [])
                
                print(f"     {j}. {variant['name']}")
                print(f"        Stock: {variant_stock}")
                if variant_colors:
                    print(f"        Цвета: {', '.join(variant_colors)}")
                if variant_sizes:
                    print(f"        Размеры: {', '.join(variant_sizes)}")
        else:
            products_without_variants += 1
            print(f"   Варианты: нет")
        
        print("-" * 60)
    
    # Итоговая статистика
    print("\n" + "=" * 80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 80)
    print(f"Всего товаров: {len(products)}")
    print(f"Товаров с вариантами: {products_with_variants}")
    print(f"Товаров без вариантов: {products_without_variants}")
    print(f"Всего вариантов: {total_variants}")
    print(f"Всего уникальных цветов: {total_colors}")
    print(f"Всего уникальных размеров: {total_sizes}")
    
    # Проверяем соответствие
    print(f"\n🔍 ПРОВЕРКА СООТВЕТСТВИЯ:")
    print("-" * 40)
    
    for i, product in enumerate(products, 1):
        colors_count = len(product['available_colors'])
        sizes_count = len(product['available_sizes'])
        variants_count = len(product['variants'])
        
        # Ожидаемое количество вариантов
        expected_variants = max(1, colors_count) * max(1, sizes_count)
        if colors_count == 0 and sizes_count == 0:
            expected_variants = 1
        
        status = "✅" if variants_count == expected_variants else "❌"
        print(f"{status} {product['name']}: ожидается {expected_variants}, есть {variants_count}")

if __name__ == "__main__":
    analyze_bot_data()

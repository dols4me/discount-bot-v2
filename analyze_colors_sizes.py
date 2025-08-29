#!/usr/bin/env python3
"""
Скрипт для анализа всех цветов и размеров из МойСклад
"""

import asyncio
import json
from moysklad_api import MoySkladAPI
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

async def analyze_colors_and_sizes():
    """Анализируем все цвета и размеры из МойСклад"""
    
    # Инициализируем API
    moysklad = MoySkladAPI()
    
    print("🔍 Анализируем все товары из МойСклад...")
    
    # Получаем все товары
    products = await moysklad.get_products(limit=1000, offset=0)
    
    print(f"📦 Получено товаров: {len(products)}")
    
    # Собираем все уникальные цвета и размеры
    all_colors = set()
    all_sizes = set()
    color_size_combinations = []
    
    for product in products:
        product_name = product.get('name', '')
        variants = product.get('variants', [])
        
        print(f"\n🔍 Товар: {product_name}")
        
        for variant in variants:
            variant_name = variant.get('name', '')
            variant_stock = variant.get('stock', 0)
            
            print(f"  📋 Вариант: {variant_name} (остаток: {variant_stock})")
            
            # Извлекаем характеристики
            if variant.get('characteristics'):
                for char in variant['characteristics']:
                    char_name = char.get('name', '').lower()
                    char_value = char.get('value', '')
                    
                    if 'размер' in char_name or 'size' in char_name:
                        all_sizes.add(char_value)
                        print(f"    📏 Размер: '{char_value}' (из характеристик)")
                    elif 'цвет' in char_name or 'color' in char_name:
                        all_colors.add(char_value)
                        print(f"    🎨 Цвет: '{char_value}' (из характеристик)")
            
            # Извлекаем из названия модификации
            name_modifications = moysklad._extract_modifications(variant_name)
            if name_modifications.get('size'):
                all_sizes.add(name_modifications['size'])
                print(f"    📏 Размер: '{name_modifications['size']}' (из названия)")
            if name_modifications.get('color'):
                all_colors.add(name_modifications['color'])
                print(f"    🎨 Цвет: '{name_modifications['color']}' (из названия)")
            
            # Сохраняем комбинацию
            if name_modifications.get('color') and name_modifications.get('size'):
                color_size_combinations.append({
                    'product': product_name,
                    'variant': variant_name,
                    'color': name_modifications['color'],
                    'size': name_modifications['size'],
                    'stock': variant_stock
                })
    
    # Сортируем для удобства
    all_colors = sorted(list(all_colors))
    all_sizes = sorted(list(all_sizes))
    
    print(f"\n🎯 РЕЗУЛЬТАТ АНАЛИЗА:")
    print(f"📊 Всего уникальных цветов: {len(all_colors)}")
    print(f"📊 Всего уникальных размеров: {len(all_sizes)}")
    
    print(f"\n🎨 ВСЕ ЦВЕТА:")
    for i, color in enumerate(all_colors, 1):
        print(f"  {i:2d}. '{color}'")
    
    print(f"\n📏 ВСЕ РАЗМЕРЫ:")
    for i, size in enumerate(all_sizes, 1):
        print(f"  {i:2d}. '{size}'")
    
    print(f"\n🔗 КОМБИНАЦИИ ЦВЕТ-РАЗМЕР:")
    for combo in color_size_combinations:
        print(f"  🎨 {combo['color']} + 📏 {combo['size']} = {combo['stock']} шт. ({combo['product']})")
    
    # Сохраняем результат в файл
    result = {
        'total_products': len(products),
        'total_colors': len(all_colors),
        'total_sizes': len(all_sizes),
        'colors': all_colors,
        'sizes': all_sizes,
        'combinations': color_size_combinations
    }
    
    with open('colors_sizes_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результат сохранен в файл 'colors_sizes_analysis.json'")
    
    return result

if __name__ == "__main__":
    asyncio.run(analyze_colors_and_sizes())

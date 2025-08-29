#!/usr/bin/env python3
"""
Скрипт для прямой проверки вариантов товаров через MoySklad API
"""

import requests
import json
from config import MOYSKLAD_API_TOKEN

def check_moysklad_variants():
    """Проверяет варианты товаров напрямую через MoySklad API"""
    
    print("🔍 Проверяем варианты товаров через MoySklad API...")
    print("=" * 80)
    
    # Токен для MoySklad
    headers = {
        'Authorization': f'Bearer {MOYSKLAD_API_TOKEN}',
        'Accept': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip'
    }
    
    # Список ID товаров для проверки
    product_ids = [
        "0144845b-9a8e-11ef-0a80-15fa005d533b",  # Джинсы Mom Fit grey
        "01e8f0af-c5b5-11ef-0a80-058e00163a1d",  # Ремень
        "03af74db-9abd-11ef-0a80-0e4b0007e09a",  # Джемпер V из вискозы
        "0b6df7f2-f5bf-11ef-0a80-0f6500490d89",  # Блузка из шелка ITCL
        "0e307f70-d313-11ef-0a80-0d1a001bbc3c",  # Жакет ITCL
        "0e3af4ca-d313-11ef-0a80-0d1a001bbc4d",  # Брюки ITCL
        "0e4970e7-d313-11ef-0a80-0d1a001bbc6a",  # Юбка женская
        "0e4ff18f-d313-11ef-0a80-0d1a001bbc74",  # Жакет Denim
        "0e5d210d-d313-11ef-0a80-0d1a001bbc88",  # Поло
        "0fb33b93-9a88-11ef-0a80-15fa0058a801"   # Брюки женские
    ]
    
    for i, product_id in enumerate(product_ids, 1):
        print(f"\n{i}. Проверяем товар ID: {product_id}")
        print("-" * 60)
        
        try:
            # Получаем информацию о товаре
            product_url = f"https://api.moysklad.ru/api/remap/1.2/entity/product/{product_id}"
            product_response = requests.get(product_url, headers=headers)
            
            if product_response.status_code == 200:
                product_data = product_response.json()
                print(f"   Название: {product_data.get('name', 'N/A')}")
                print(f"   Артикул: {product_data.get('article', 'N/A')}")
                
                # Получаем варианты товара
                variants_url = f"https://api.moysklad.ru/api/remap/1.2/entity/variant?filter=product.id={product_id}"
                variants_response = requests.get(variants_url, headers=headers)
                
                if variants_response.status_code == 200:
                    variants_data = variants_response.json()
                    variants_count = len(variants_data.get('rows', []))
                    print(f"   Вариантов в MoySklad: {variants_count}")
                    
                    # Показываем детали вариантов
                    for j, variant in enumerate(variants_data.get('rows', []), 1):
                        variant_name = variant.get('name', 'N/A')
                        variant_id = variant.get('id', 'N/A')
                        print(f"     Вариант {j}: {variant_name} (ID: {variant_id})")
                        
                        # Проверяем характеристики
                        characteristics = variant.get('characteristics', [])
                        if characteristics:
                            print(f"       Характеристики:")
                            for char in characteristics:
                                char_name = char.get('name', 'N/A')
                                char_value = char.get('value', 'N/A')
                                print(f"         {char_name}: {char_value}")
                else:
                    print(f"   ❌ Ошибка получения вариантов: {variants_response.status_code}")
                    
            else:
                print(f"   ❌ Ошибка получения товара: {product_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    check_moysklad_variants()

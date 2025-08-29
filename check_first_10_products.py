#!/usr/bin/env python3
"""
Скрипт для проверки первых 10 товаров и сравнения количества модификаций с MoySklad
"""

import requests
import json
from moysklad_api import MoySkladAPI
from config import MOYSKLAD_API_TOKEN

def check_first_10_products():
    """Проверяет первые 10 товаров и сравнивает с MoySklad"""
    
    print("🔍 Проверяем первые 10 товаров в боте...")
    print("=" * 80)
    
    # Получаем данные из бота
    try:
        response = requests.get("http://localhost:8000/api/products?limit=10&offset=0")
        if response.status_code == 200:
            bot_data = response.json()['products']
        else:
            print(f"❌ Ошибка получения данных из бота: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
        return
    
    # Инициализируем MoySklad API
    try:
        moysklad = MoySkladAPI(MOYSKLAD_API_TOKEN)
        print("✅ MoySklad API инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации MoySklad API: {e}")
        return
    
    print("\n📊 Сравнение данных:")
    print("-" * 80)
    
    for i, product in enumerate(bot_data, 1):
        print(f"\n{i}. {product['name']}")
        print(f"   ID: {product['original_id']}")
        print(f"   Stock в боте: {product['stock']}")
        print(f"   Цвета в боте: {len(product['available_colors'])} - {product['available_colors']}")
        print(f"   Размеры в боте: {len(product['available_sizes'])} - {product['available_sizes']}")
        print(f"   Варианты в боте: {len(product['variants'])}")
        
        # Проверяем варианты детально
        for j, variant in enumerate(product['variants'], 1):
            print(f"     Вариант {j}: {variant['name']} - Stock: {variant['stock']}")
        
        print("-" * 40)

if __name__ == "__main__":
    check_first_10_products()

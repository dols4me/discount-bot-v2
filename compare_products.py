#!/usr/bin/env python3
"""
Скрипт для сравнения двух ID одного товара
"""

import asyncio
import aiohttp
import requests
from moysklad_api import MoySkladAPI

async def compare_products():
    """Сравниваем два ID одного товара"""
    
    # Создаем экземпляр API
    api = MoySkladAPI()
    
    # Получаем новый токен и обновляем заголовки
    new_token = api.get_access_token()
    if new_token:
        api.api_token = new_token
        api.headers['Authorization'] = f'Bearer {new_token}'
        print(f"✅ Обновлен токен в API: {new_token[:20]}...")
    
    # Два ID одного товара
    product_id_1 = "c2a51d97-affd-11ef-0a80-197800bf411a"  # В нашем приложении
    product_id_2 = "c2a22d50-affd-11ef-0a80-197800bf4115"  # В МойСклад с изображением
    
    print("🔍 Сравниваем два ID одного товара:")
    print(f"   ID 1 (в приложении): {product_id_1}")
    print(f"   ID 2 (с изображением): {product_id_2}")
    
    # Проверяем первый товар
    print(f"\n📦 Проверяем товар 1: {product_id_1}")
    product_1 = await api._get_product_detail(product_id_1)
    
    if product_1:
        print(f"✅ Товар 1 найден: {product_1.get('name')}")
        print(f"📄 Изображения: {product_1.get('images')}")
        
        if product_1.get('images', {}).get('rows'):
            print(f"🖼️ Количество изображений: {len(product_1['images']['rows'])}")
        else:
            print(f"❌ Нет изображений")
            
        # Проверяем модификации
        if product_1.get('variants'):
            print(f"🔍 Модификации: {len(product_1['variants'])} шт.")
            for i, variant in enumerate(product_1['variants']):
                print(f"   Модификация {i+1}: {variant.get('name')} (ID: {variant.get('id')})")
                if variant.get('images'):
                    print(f"   🖼️ Есть изображения в модификации")
                else:
                    print(f"   ❌ Нет изображений в модификации")
    else:
        print(f"❌ Товар 1 не найден")
    
    # Проверяем второй товар
    print(f"\n📦 Проверяем товар 2: {product_id_2}")
    product_2 = await api._get_product_detail(product_id_2)
    
    if product_2:
        print(f"✅ Товар 2 найден: {product_2.get('name')}")
        print(f"📄 Изображения: {product_2.get('images')}")
        
        if product_2.get('images', {}).get('rows'):
            print(f"🖼️ Количество изображений: {len(product_2['images']['rows'])}")
            for i, image in enumerate(product_2['images']['rows']):
                print(f"   Изображение {i+1}: {image.get('filename')}")
                if image.get('meta', {}).get('downloadHref'):
                    print(f"   🔗 URL: {image['meta']['downloadHref']}")
        else:
            print(f"❌ Нет изображений")
    else:
        print(f"❌ Товар 2 не найден")

if __name__ == "__main__":
    print("🚀 Запуск сравнения товаров")
    asyncio.run(compare_products())

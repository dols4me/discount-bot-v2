#!/usr/bin/env python3
"""
Скрипт для проверки всех товаров на наличие изображений
"""

import asyncio
import aiohttp
import requests
from moysklad_api import MoySkladAPI

async def check_all_products_for_images():
    """Проверяем все товары на наличие изображений"""
    
    # Создаем экземпляр API
    api = MoySkladAPI()
    
    # Получаем новый токен и обновляем заголовки
    new_token = api.get_access_token()
    if new_token:
        api.api_token = new_token
        api.headers['Authorization'] = f'Bearer {new_token}'
        print(f"✅ Обновлен токен в API: {new_token[:20]}...")
    
    # Получаем все товары
    print("📦 Получаем все товары...")
    all_products = await api.get_products(limit=1000, offset=0)
    
    if not all_products:
        print("❌ Не удалось получить товары")
        return
    
    print(f"✅ Получено товаров: {len(all_products)}")
    
    # Проверяем первые 100 товаров на наличие изображений
    products_with_images = []
    products_without_images = []
    
    print(f"🔍 Проверяем первые 100 товаров на наличие изображений...")
    
    for i, product in enumerate(all_products[:100]):
        try:
            print(f"🔍 Проверяем товар {i+1}/100: {product.get('name')}")
            
            # Получаем детальную информацию о товаре
            product_detail = await api._get_product_detail(product.get('original_id'))
            
            if product_detail:
                # Проверяем изображения
                if product_detail.get('images') and product_detail['images'].get('rows'):
                    image_count = len(product_detail['images']['rows'])
                    if image_count > 0:
                        print(f"✅ Найдены изображения: {image_count} шт.")
                        products_with_images.append({
                            'name': product.get('name'),
                            'id': product.get('original_id'),
                            'image_count': image_count
                        })
                    else:
                        print(f"❌ Нет изображений (rows пустой)")
                        products_without_images.append(product.get('name'))
                else:
                    print(f"❌ Нет структуры изображений")
                    products_without_images.append(product.get('name'))
            else:
                print(f"❌ Не удалось получить детали товара")
                products_without_images.append(product.get('name'))
                
        except Exception as e:
            print(f"⚠️ Ошибка проверки товара {product.get('name')}: {e}")
            products_without_images.append(product.get('name'))
    
    # Выводим результаты
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("="*50)
    
    print(f"🔍 Проверено товаров: 100")
    print(f"✅ Товаров с изображениями: {len(products_with_images)}")
    print(f"❌ Товаров без изображений: {len(products_without_images)}")
    
    if products_with_images:
        print(f"\n🖼️ ТОВАРЫ С ИЗОБРАЖЕНИЯМИ:")
        for product in products_with_images:
            print(f"   📸 {product['name']} (ID: {product['id']}) - {product['image_count']} изображений")
    
    print(f"\n📋 ПЕРВЫЕ 10 ТОВАРОВ БЕЗ ИЗОБРАЖЕНИЙ:")
    for i, name in enumerate(products_without_images[:10]):
        print(f"   {i+1}. {name}")

if __name__ == "__main__":
    print("🚀 Запуск проверки всех товаров на наличие изображений")
    asyncio.run(check_all_products_for_images())

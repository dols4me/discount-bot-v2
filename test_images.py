#!/usr/bin/env python3
"""
Тестовый скрипт для проверки получения изображений товара
"""

import asyncio
import aiohttp
import requests
import base64
from moysklad_api import MoySkladAPI

async def test_product_images():
    """Тестируем получение изображений товара"""
    
    # Создаем экземпляр API
    api = MoySkladAPI()
    
    # Получаем новый токен и обновляем заголовки
    new_token = api.get_access_token()
    if new_token:
        api.api_token = new_token
        api.headers['Authorization'] = f'Bearer {new_token}'
        print(f"✅ Обновлен токен в API: {new_token[:20]}...")
    
    # Получаем список товаров
    print("📦 Получаем список товаров...")
    products = await api.get_products(limit=10, offset=0)
    
    if products:
        print(f"✅ Получено товаров: {len(products)}")
        
        # Берем первый товар для тестирования
        first_product = products[0]
        product_id = first_product.get('original_id')
        print(f"🔍 Тестируем первый товар: {first_product.get('name')} (ID: {product_id})")
    else:
        print("❌ Не удалось получить список товаров")
        return
    
    print(f"🔍 Тестируем получение изображений для товара: {product_id}")
    
    # Получаем детальную информацию о товаре
    product_detail = await api._get_product_detail(product_id)
    
    if product_detail:
        print(f"✅ Получена детальная информация о товаре: {product_detail.get('name')}")
        print(f"📄 Ключи в ответе: {list(product_detail.keys())}")
        
        # Проверяем изображения
        if product_detail.get('images'):
            print(f"🖼️ Найдены изображения в товаре")
            print(f"📄 Структура images: {list(product_detail['images'].keys())}")
            
            if product_detail['images'].get('rows'):
                print(f"📄 Количество изображений: {len(product_detail['images']['rows'])}")
                
                for i, image in enumerate(product_detail['images']['rows']):
                    print(f"🖼️ Изображение {i+1}:")
                    print(f"   📄 Поля: {list(image.keys())}")
                    print(f"   📄 Meta: {list(image.get('meta', {}).keys())}")
                    
                    # Проверяем различные способы получения URL
                    if image.get('meta', {}).get('downloadHref'):
                        print(f"   ✅ downloadHref: {image['meta']['downloadHref']}")
                    
                    if image.get('miniature', {}).get('href'):
                        print(f"   ✅ miniature.href: {image['miniature']['href']}")
                    
                    if image.get('content'):
                        print(f"   ✅ content: Base64 данные (длина: {len(image['content'])})")
            else:
                print(f"❌ Нет rows в images")
        else:
            print(f"❌ Изображения не найдены в товаре")
    else:
        print(f"❌ Не удалось получить детальную информацию о товаре")

def test_token():
    """Тестируем получение нового токена"""
    print("🔑 Тестируем получение нового токена...")
    
    api = MoySkladAPI()
    new_token = api.get_access_token()
    
    if new_token:
        print(f"✅ Получен новый токен: {new_token[:20]}...")
        return new_token
    else:
        print("❌ Не удалось получить новый токен")
        return None

if __name__ == "__main__":
    print("🚀 Запуск тестирования изображений товаров")
    
    # Тестируем токен
    token = test_token()
    
    if token:
        # Тестируем изображения
        asyncio.run(test_product_images())
    else:
        print("❌ Не можем продолжить без токена")

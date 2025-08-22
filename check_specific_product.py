#!/usr/bin/env python3
"""
Скрипт для проверки конкретного товара с изображениями
"""

import asyncio
import aiohttp
import requests
from moysklad_api import MoySkladAPI

async def check_specific_product():
    """Проверяем конкретный товар с изображениями"""
    
    # Создаем экземпляр API
    api = MoySkladAPI()
    
    # Получаем новый токен и обновляем заголовки
    new_token = api.get_access_token()
    if new_token:
        api.api_token = new_token
        api.headers['Authorization'] = f'Bearer {new_token}'
        print(f"✅ Обновлен токен в API: {new_token[:20]}...")
    
    # ID товара с изображениями
    product_id = "c2a22d50-affd-11ef-0a80-197800bf4115"
    
    print(f"🔍 Проверяем товар с изображениями: {product_id}")
    
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
                        
                    # Пробуем получить изображение через downloadHref
                    if image.get('meta', {}).get('downloadHref'):
                        download_url = image['meta']['downloadHref']
                        print(f"   🔗 Пробуем скачать изображение: {download_url}")
                        
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(download_url, headers=api.headers) as response:
                                    if response.status == 200:
                                        print(f"   ✅ Изображение успешно загружено (размер: {len(await response.read())} байт)")
                                    else:
                                        print(f"   ❌ Ошибка загрузки изображения: {response.status}")
                        except Exception as e:
                            print(f"   ❌ Ошибка при загрузке изображения: {e}")
            else:
                print(f"❌ Нет rows в images")
        else:
            print(f"❌ Изображения не найдены в товаре")
    else:
        print(f"❌ Не удалось получить детальную информацию о товаре")

if __name__ == "__main__":
    print("🚀 Запуск проверки конкретного товара с изображениями")
    asyncio.run(check_specific_product())

#!/usr/bin/env python3
"""
Скрипт для поиска конкретного товара в исходных данных МойСклад
"""

import asyncio
import aiohttp
import requests
from moysklad_api import MoySkladAPI

async def find_specific_product():
    """Ищем конкретный товар в исходных данных"""
    
    # Создаем экземпляр API
    api = MoySkladAPI()
    
    # Получаем новый токен и обновляем заголовки
    new_token = api.get_access_token()
    if new_token:
        api.api_token = new_token
        api.headers['Authorization'] = f'Bearer {new_token}'
        print(f"✅ Обновлен токен в API: {new_token[:20]}...")
    
    # ID товара с изображениями
    target_product_id = "c2a22d50-affd-11ef-0a80-197800bf4115"
    
    print(f"🔍 Ищем товар: {target_product_id}")
    
    # Получаем все товары из отчета об остатках
    print("📦 Получаем все товары из отчета об остатках...")
    
    url = f"{api.base_url}/report/stock/all"
    params = {'limit': 1000, 'offset': 0}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=api.headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Получено товаров из отчета: {len(data.get('rows', []))}")
                
                # Ищем наш товар
                found_product = None
                for i, item in enumerate(data.get('rows', [])):
                    product_id = item.get('meta', {}).get('href', '').split('/')[-1].split('?')[0]
                    if product_id == target_product_id:
                        found_product = item
                        print(f"✅ Товар найден на позиции {i+1}: {item.get('name')}")
                        print(f"📄 Остаток: {item.get('stock', 0)}")
                        break
                
                if found_product:
                    print(f"📦 Название: {found_product.get('name')}")
                    print(f"📄 Остаток: {found_product.get('stock', 0)}")
                    print(f"💰 Цена: {found_product.get('salePrice', 0)}")
                    
                    # Проверяем, почему товар не попадает в финальный список
                    stock = found_product.get('stock', 0)
                    if stock <= 0:
                        print(f"❌ Товар не попадает в список из-за нулевого остатка: {stock}")
                    else:
                        print(f"✅ Товар должен попадать в список (остаток: {stock})")
                else:
                    print(f"❌ Товар не найден в отчете об остатках")
                    
                    # Попробуем получить товар напрямую
                    print("🔍 Пробуем получить товар напрямую...")
                    product_detail = await api._get_product_detail(target_product_id)
                    if product_detail:
                        print(f"✅ Товар найден напрямую: {product_detail.get('name')}")
                        print(f"📄 Остаток: {product_detail.get('stock', 'не указан')}")
                    else:
                        print(f"❌ Товар не найден даже напрямую")
            else:
                print(f"❌ Ошибка получения отчета: {response.status}")

if __name__ == "__main__":
    print("🚀 Запуск поиска конкретного товара")
    asyncio.run(find_specific_product())

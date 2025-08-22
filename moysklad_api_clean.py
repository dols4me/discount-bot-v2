import aiohttp
import time
import re
from typing import List, Dict, Any, Optional

class MoySkladAPI:
    def __init__(self, api_token: str = None):
        self.api_token = api_token
        self.base_url = "https://api.moysklad.ru/api/remap/1.2"
        self.headers = {
            'Authorization': f'Bearer {api_token}' if api_token else '',
            'Accept': 'application/json;charset=utf-8',
            'Accept-Encoding': 'gzip'
        }
        
        # Кэширование
        self._products_cache = []
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 минут
        
        # Инициализация базы данных
        from database import Database
        self.db = Database()

    def _is_cache_valid(self):
        """Проверка валидности кэша"""
        return (time.time() - self._cache_timestamp) < self._cache_ttl

    def _get_cached_products(self, limit: int, offset: int) -> List[Dict]:
        """Получение товаров из кэша с пагинацией"""
        start = offset
        end = offset + limit
        return self._products_cache[start:end]

    def clear_cache(self):
        """Очистка кэша товаров"""
        self._products_cache = []
        self._cache_timestamp = 0
        print("🗑️ Кэш товаров очищен")

    def force_refresh_products(self):
        """Принудительное обновление кэша товаров"""
        self.clear_cache()
        print("🔄 Принудительное обновление кэша товаров")

    async def get_products(self, limit=50, offset=0):
        """Получение списка товаров с кэшированием"""
        print(f"🔍 Запрос товаров: limit={limit}, offset={offset}")
        
        # Проверяем кэш
        if self._is_cache_valid():
            print(f"⚡ Используем кэш товаров (возраст: {int(time.time() - self._cache_timestamp)}с)")
            return self._get_cached_products(limit, offset)
        
        print("🔄 Кэш устарел, загружаем новые данные...")
        
        try:
            # Получаем остатки товаров
            stock_data = await self._get_stock_data()
            print(f"📦 Получено остатков: {len(stock_data)} позиций")
            
            # Получаем детальную информацию о товарах
            products_data = await self._get_products_data()
            print(f"🛍️ Получено товаров: {len(products_data)} позиций")
            
            # Объединяем данные
            products = self._merge_stock_and_products(stock_data, products_data)
            print(f"✅ Обработано товаров: {len(products)}")
            
            # Кэшируем результат
            self._products_cache = products
            self._cache_timestamp = time.time()
            print(f"💾 Товары закэшированы ({len(products)} шт.)")
            
            return self._get_cached_products(limit, offset)
            
        except Exception as e:
            print(f"❌ Ошибка получения товаров: {e}")
            import traceback
            traceback.print_exc()
            return self._get_test_products()

    async def _get_stock_data(self):
        """Получение остатков товаров из /report/stock/bystore/current"""
        print("📊 Загружаем остатки товаров...")
        
        if not self.api_token:
            print("⚠️ API токен МойСклад отсутствует")
            return []

        try:
            url = f"{self.base_url}/report/stock/bystore/current"
            
            print(f"📡 Запрос остатков к: {url}")
            print(f"🔑 Headers: {self.headers}")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    print(f"📊 Статус ответа: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print(f"📦 Получено данных: {len(data.get('rows', []))} товаров")
                        print(f"📄 Структура ответа: {list(data.keys())}")
                        
                        if data.get('rows'):
                            first_item = data['rows'][0]
                            print(f"🔍 Первый товар: {first_item}")
                        
                        return data.get('rows', [])
                    else:
                        error_text = await response.text()
                        print(f"❌ Ошибка API МойСклад при получении остатков: {response.status}")
                        print(f"📄 Текст ошибки: {error_text}")
                        return []

        except Exception as e:
            print(f"💥 Исключение при получении остатков: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def _get_products_data(self):
        """Получение детальной информации о товарах из /entity/product"""
        print("🛍️ Загружаем детальную информацию о товарах...")
        
        if not self.api_token:
            print("⚠️ API токен МойСклад отсутствует")
            return []

        try:
            url = f"{self.base_url}/entity/product"
            params = {'limit': 1000, 'offset': 0}
            
            print(f"📡 Запрос товаров к: {url}")
            print(f"🔑 Headers: {self.headers}")
            print(f"📝 Params: {params}")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    print(f"📊 Статус ответа товаров: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print(f"🛍️ Получено товаров: {len(data.get('rows', []))} позиций")
                        print(f"📄 Структура ответа товаров: {list(data.keys())}")
                        
                        if data.get('rows'):
                            first_item = data['rows'][0]
                            print(f"🔍 Первый товар: {first_item}")
                        
                        return data.get('rows', [])
                    else:
                        error_text = await response.text()
                        print(f"❌ Ошибка API МойСклад при получении товаров: {response.status}")
                        print(f"📄 Текст ошибки: {error_text}")
                        return []

        except Exception as e:
            print(f"💥 Исключение при получении товаров: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _merge_stock_and_products(self, stock_data, products_data):
        """Объединение данных об остатках и товарах"""
        print("🔗 Объединяем данные об остатках и товарах...")
        
        # Создаем словарь товаров по ID
        products_dict = {}
        for product in products_data:
            product_id = product.get('id')
            if product_id:
                products_dict[product_id] = product
        
        print(f"📋 Создан словарь товаров: {len(products_dict)} позиций")
        
        # Обрабатываем остатки
        result_products = []
        
        for stock_item in stock_data:
            try:
                # Получаем ID товара из остатков
                product_id = stock_item.get('meta', {}).get('href', '').split('/')[-1].split('?')[0]
                
                # Получаем информацию о товаре
                product_info = products_dict.get(product_id)
                
                if not product_info:
                    print(f"⚠️ Товар не найден: {product_id}")
                    continue
                
                # Получаем остаток
                stock = stock_item.get('stock', 0)
                
                # Пропускаем товары без остатков
                if stock <= 0:
                    continue
                
                # Получаем цену
                price = 0
                if stock_item.get('salePrice'):
                    price = stock_item['salePrice'] / 100
                
                # Определяем категорию
                category = 'other'
                if product_info.get('productFolder') and product_info['productFolder'].get('name'):
                    category = product_info['productFolder']['name']
                
                # Создаем товар
                product = {
                    'id': product_info.get('name', 'Без названия'),
                    'original_id': product_id,
                    'name': product_info.get('name', 'Без названия'),
                    'description': product_info.get('description', ''),
                    'article': product_info.get('article', ''),
                    'price': int(price),
                    'image': None,
                    'stock': int(stock),
                    'category': category,
                    'modifications_text': f"В наличии: {int(stock)}",
                    'available_colors': [],
                    'available_sizes': []
                }
                
                # Добавляем изображение, если есть
                if product_info.get('images') and product_info['images'].get('rows'):
                    image = product_info['images']['rows'][0]
                    if image.get('meta', {}).get('downloadHref'):
                        download_url = image['meta']['downloadHref']
                        if '/download/' in download_url:
                            image_id = download_url.split('/')[-1]
                            product['image'] = f"/proxy/image/{image_id}"
                
                result_products.append(product)
                
            except Exception as e:
                print(f"⚠️ Ошибка обработки товара: {e}")
                continue
        
        print(f"✅ Обработано товаров: {len(result_products)}")
        return result_products

    async def get_categories(self):
        """Получение списка категорий из МойСклад"""
        print("🔍 Запрос категорий из МойСклад...")
        
        if not self.api_token:
            print("⚠️ API токен МойСклад отсутствует")
            return self._get_test_categories()

        try:
            url = f"{self.base_url}/entity/productfolder"
            params = {'limit': 1000, 'offset': 0}
            
            print(f"📡 Запрос категорий к: {url}")
            print(f"🔑 Headers: {self.headers}")
            print(f"📝 Params: {params}")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    print(f"📊 Статус ответа категорий: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print(f"📦 Получено категорий: {len(data.get('rows', []))}")
                        print(f"📄 Структура ответа категорий: {list(data.keys())}")
                        
                        if data.get('rows'):
                            first_item = data['rows'][0]
                            print(f"🔍 Первая категория: {first_item}")
                        
                        categories = []
                        for item in data.get('rows', []):
                            categories.append({
                                'id': item.get('id'),
                                'name': item.get('name', 'Без названия')
                            })
                        
                        return categories
                    else:
                        error_text = await response.text()
                        print(f"❌ Ошибка API МойСклад при получении категорий: {response.status}")
                        print(f"📄 Текст ошибки: {error_text}")
                        return self._get_test_categories()

        except Exception as e:
            print(f"💥 Исключение при получении категорий: {e}")
            import traceback
            traceback.print_exc()
            return self._get_test_categories()

    async def get_product_by_id(self, product_id):
        """Получение товара по ID"""
        print(f"🔍 Поиск товара по ID: {product_id}")
        
        try:
            # Получаем все товары и ищем нужный
            products = await self.get_products(limit=1000, offset=0)
            
            # Ищем товар по ID
            for product in products:
                if product.get('original_id') == product_id:
                    print(f"✅ Товар найден: {product.get('name')}")
                    return product
            
            print(f"❌ Товар не найден для ID: {product_id}")
            return None
            
        except Exception as e:
            print(f"💥 Ошибка поиска товара: {e}")
            return None

    def _get_test_categories(self):
        """Тестовые категории для демонстрации"""
        return [
            {'id': 'cat_1', 'name': 'Электроника'},
            {'id': 'cat_2', 'name': 'Одежда'},
            {'id': 'cat_3', 'name': 'Обувь'},
            {'id': 'cat_4', 'name': 'Аксессуары'}
        ]

    def _get_test_products(self):
        """Тестовые данные товаров для демонстрации"""
        return [
            {
                'id': 'test_1',
                'name': 'Смартфон iPhone 15',
                'description': 'Новейший iPhone с отличной камерой',
                'price': 89990.0,
                'image': None,
                'stock': 10,
                'category': 'electronics'
            },
            {
                'id': 'test_2',
                'name': 'Ноутбук MacBook Air',
                'description': 'Легкий и мощный ноутбук',
                'price': 129990.0,
                'image': None,
                'stock': 5,
                'category': 'electronics'
            }
        ]

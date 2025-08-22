import aiohttp
import time
import re
from typing import List, Dict, Any, Optional

class MoySkladAPI:
    def __init__(self, api_token: str = None):
        if api_token is None:
            from config import MOYSKLAD_API_TOKEN
            api_token = MOYSKLAD_API_TOKEN
            
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
        
        # Кэш для изображений
        self._images_cache = {}
        self._images_cache_ttl = 3600  # 1 час для изображений
        
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
    
    def clear_images_cache(self):
        """Очистка кэша изображений"""
        self._images_cache.clear()
        print("🗑️ Кэш изображений очищен")
    
    def _is_image_cache_valid(self, image_id: str) -> bool:
        """Проверка валидности кэша изображения"""
        if image_id not in self._images_cache:
            return False
        cache_entry = self._images_cache[image_id]
        return (time.time() - cache_entry['timestamp']) < self._images_cache_ttl

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
            # Получаем родительские товары (products)
            products_data = await self._get_products_info()
            print(f"🛍️ Получено родительских товаров: {len(products_data)}")
            
            # Получаем модификации (variants) для каждого товара
            variants_data = await self._get_variants()
            print(f"🔄 Получено модификаций: {len(variants_data)}")
            
            # Получаем остатки
            stock_data = await self._get_stock_all()
            print(f"📊 Получено остатков: {len(stock_data)}")
            
            # Объединяем данные
            products = await self._merge_products_with_variants_and_stock(products_data, variants_data, stock_data)
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

    async def _get_products_info(self):
        """Получение информации о родительских товарах"""
        print("🛍️ Загружаем родительские товары...")
        
        if not self.api_token:
            print("⚠️ API токен МойСклад отсутствует")
            return []

        try:
            url = f"{self.base_url}/entity/product"
            params = {'limit': 2000}  # Увеличиваем лимит
            
            print(f"📡 Запрос товаров к: {url}")
            print(f"🔑 Headers: {self.headers}")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    print(f"📊 Статус ответа товаров: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print(f"📦 Получено товаров: {len(data.get('rows', []))}")
                        
                        if data.get('rows'):
                            first_item = data['rows'][0]
                            print(f"🔍 Первый товар: {first_item.get('name', 'Unknown')}")
                        
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

    async def _get_variants(self):
        """Получение модификаций (variants) с расширенной информацией"""
        print("🔄 Загружаем модификации товаров...")
        
        if not self.api_token:
            print("⚠️ API токен МойСклад отсутствует")
            return []

        try:
            url = f"{self.base_url}/entity/variant"
            params = {
                'limit': 1000,  # Максимальный лимит за запрос
                'expand': 'product'  # Получаем информацию о родительском товаре
            }
            
            print(f"📡 Запрос модификаций к: {url}")
            print(f"🔑 Headers: {self.headers}")

            all_variants = []
            offset = 0
            
            async with aiohttp.ClientSession() as session:
                while True:
                    params['offset'] = offset
                    
                    async with session.get(url, headers=self.headers, params=params) as response:
                        print(f"📊 Статус ответа модификаций (offset={offset}): {response.status}")

                        if response.status == 200:
                            data = await response.json()
                            variants = data.get('rows', [])
                            
                            if not variants:
                                break
                            
                            all_variants.extend(variants)
                            print(f"📦 Получено модификаций в этом запросе: {len(variants)}")
                            
                            if len(variants) < 1000:
                                break
                            
                            offset += 1000
                        else:
                            error_text = await response.text()
                            print(f"❌ Ошибка API МойСклад при получении модификаций: {response.status}")
                            print(f"📄 Текст ошибки: {error_text}")
                            break

            print(f"📦 Всего получено модификаций: {len(all_variants)}")
            
            if all_variants:
                first_item = all_variants[0]
                print(f"🔍 Первая модификация: {first_item.get('name', 'Unknown')}")
            
            return all_variants

        except Exception as e:
            print(f"💥 Исключение при получении модификаций: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def _get_stock_all(self):
        """Получение остатков товаров из /report/stock/all"""
        print("📊 Загружаем остатки товаров...")
        
        if not self.api_token:
            print("⚠️ API токен МойСклад отсутствует")
            return []

        try:
            url = f"{self.base_url}/report/stock/all"
            params = {
                'limit': 1000,  # Максимальный лимит за запрос
            }
            
            print(f"📡 Запрос остатков к: {url}")
            print(f"🔑 Headers: {self.headers}")

            all_stock = []
            offset = 0
            
            async with aiohttp.ClientSession() as session:
                while True:
                    params['offset'] = offset
                    
                    async with session.get(url, headers=self.headers, params=params) as response:
                        print(f"📊 Статус ответа остатков (offset={offset}): {response.status}")

                        if response.status == 200:
                            data = await response.json()
                            stock_items = data.get('rows', [])
                            
                            if not stock_items:
                                break
                            
                            all_stock.extend(stock_items)
                            print(f"📦 Получено остатков в этом запросе: {len(stock_items)}")
                            
                            if len(stock_items) < 1000:
                                break
                            
                            offset += 1000
                        else:
                            error_text = await response.text()
                            print(f"❌ Ошибка API МойСклад при получении остатков: {response.status}")
                            print(f"📄 Текст ошибки: {error_text}")
                            break

            print(f"📦 Всего получено остатков: {len(all_stock)}")
            
            if all_stock:
                first_item = all_stock[0]
                print(f"🔍 Первый остаток: {first_item.get('name', 'Unknown')}")
            
            return all_stock

        except Exception as e:
            print(f"💥 Исключение при получении остатков: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def _merge_products_with_variants_and_stock(self, products_data, variants_data, stock_data):
        """Объединение данных о товарах с модификациями и остатками"""
        print("🔗 Объединяем данные о товарах с модификациями и остатками...")
        
        # Создаем словарь остатков по ID (только положительные значения)
        stock_dict = {}
        total_positive_stock = 0
        
        for stock_item in stock_data:
            try:
                # В /report/stock/all используется поле 'meta' с href
                meta_href = stock_item.get('meta', {}).get('href', '')
                if meta_href:
                    item_id = meta_href.split('/')[-1].split('?')[0]
                    
                    # В /report/stock/all используется поле 'quantity'
                    quantity = stock_item.get('quantity', 0)
                    
                    # Берем только положительные значения
                    if quantity > 0:
                        stock_dict[item_id] = quantity
                        total_positive_stock += quantity
            except Exception as e:
                print(f"⚠️ Ошибка обработки остатка: {e}")
                continue
        
        print(f"📋 Создан словарь остатков: {len(stock_dict)} позиций")
        print(f"📊 Общий положительный stock: {total_positive_stock}")
        
        # Группируем модификации по родительским товарам
        variants_by_product = {}
        for variant in variants_data:
            try:
                # Извлекаем ID родительского товара из meta.href
                product_id = None
                if variant.get('product'):
                    if isinstance(variant['product'], dict) and variant['product'].get('id'):
                        # Если product уже развернут (с expand)
                        product_id = variant['product']['id']
                    elif isinstance(variant['product'], dict) and variant['product'].get('meta', {}).get('href'):
                        # Если product содержит только meta
                        meta_href = variant['product']['meta']['href']
                        product_id = meta_href.split('/')[-1].split('?')[0]
                
                if product_id:
                    if product_id not in variants_by_product:
                        variants_by_product[product_id] = []
                    variants_by_product[product_id].append(variant)
            except Exception as e:
                print(f"⚠️ Ошибка группировки модификации: {e}")
                continue
        
        print(f"📋 Сгруппировано модификаций по товарам: {len(variants_by_product)}")
        
        # Создаем итоговый список товаров
        result_products = []
        
        # Обрабатываем все родительские товары
        for product in products_data:
            try:
                product_id = product.get('id')
                if not product_id:
                    continue
                
                # Получаем модификации для этого товара
                variants = variants_by_product.get(product_id, [])
                
                # Определяем категорию на основе pathName
                category = 'other'
                if product.get('pathName'):
                    category = product['pathName']
                elif product.get('productFolder') and product['productFolder'].get('name'):
                    category = product['productFolder']['name']
                
                # Извлекаем доступные размеры и цвета из модификаций
                available_sizes = []
                available_colors = []
                total_stock = 0
                
                # Если у товара есть варианты, считаем stock по вариантам
                if variants:
                    for variant in variants:
                        variant_id = variant.get('id')
                        variant_stock = stock_dict.get(variant_id, 0)
                        total_stock += variant_stock
                        
                        # Извлекаем характеристики
                        if variant.get('characteristics'):
                            for char in variant['characteristics']:
                                char_name = char.get('name', '').lower()
                                char_value = char.get('value', '')
                                
                                if 'размер' in char_name or 'size' in char_name:
                                    if self._is_valid_size(char_value) and char_value not in available_sizes:
                                        available_sizes.append(char_value)
                                elif 'цвет' in char_name or 'color' in char_name:
                                    if self._is_valid_color(char_value) and char_value not in available_colors:
                                        available_colors.append(char_value)
                    
                    # Если нет характеристик, извлекаем из названий модификаций
                    if not available_sizes and not available_colors:
                        for variant in variants:
                            name_modifications = self._extract_modifications(variant.get('name', ''))
                            if name_modifications.get('size') and name_modifications['size'] not in available_sizes:
                                available_sizes.append(name_modifications['size'])
                            if name_modifications.get('color') and name_modifications['color'] not in available_colors:
                                available_colors.append(name_modifications['color'])
                else:
                    # Если у товара нет вариантов, берем stock самого товара
                    total_stock = stock_dict.get(product_id, 0)
                
                # Получаем цену из первой модификации или из товара
                price = 0
                if variants and variants[0].get('salePrices') and variants[0]['salePrices']:
                    price = variants[0]['salePrices'][0].get('value', 0) / 100
                elif product.get('salePrices') and product['salePrices']:
                    price = product['salePrices'][0].get('value', 0) / 100
                
                # Создаем товар
                result_product = {
                    'id': product.get('name', ''),
                    'original_id': product_id,
                    'name': product.get('name', ''),
                    'description': product.get('description', ''),
                    'article': product.get('article', ''),
                    'price': int(price),
                    'image': None,
                    'stock': int(total_stock),
                    'category': category,
                    'modifications_text': f"В наличии: {int(total_stock)}",
                    'available_colors': available_colors,
                    'available_sizes': available_sizes,
                    'variants': []  # Добавляем список модификаций
                }
                
                # Добавляем модификации в товар
                for variant in variants:
                    variant_id = variant.get('id')
                    variant_stock = stock_dict.get(variant_id, 0)
                    
                    variant_data = {
                        'id': variant_id,
                        'name': variant.get('name', ''),
                        'stock': int(variant_stock),
                        'price': int(price),  # Используем цену товара
                        'sizes': [],
                        'colors': []
                    }
                    
                    # Извлекаем характеристики модификации
                    if variant.get('characteristics'):
                        for char in variant['characteristics']:
                            char_name = char.get('name', '').lower()
                            char_value = char.get('value', '')
                            
                            if 'размер' in char_name or 'size' in char_name:
                                if self._is_valid_size(char_value):
                                    variant_data['sizes'].append(char_value)
                            elif 'цвет' in char_name or 'color' in char_name:
                                if self._is_valid_color(char_value):
                                    variant_data['colors'].append(char_value)
                    
                    # Если нет характеристик, извлекаем из названия
                    if not variant_data['sizes'] and not variant_data['colors']:
                        name_modifications = self._extract_modifications(variant.get('name', ''))
                        if name_modifications.get('size'):
                            variant_data['sizes'].append(name_modifications['size'])
                        if name_modifications.get('color'):
                            variant_data['colors'].append(name_modifications['color'])
                    
                    result_product['variants'].append(variant_data)
                
                # Определяем, нужно ли отправлять в "Брак"
                if not available_sizes and not available_colors:
                    result_product['category'] = 'Брак'
                
                # Добавляем изображение, если есть
                if self._has_images(product):
                    image_url = await self._get_product_images(product)
                    result_product['image'] = image_url
                else:
                    result_product['image'] = None
                
                result_products.append(result_product)

            except Exception as e:
                print(f"⚠️ Ошибка обработки товара: {e}")
                continue
        
        print(f"✅ Обработано товаров: {len(result_products)}")
        
        # Проверяем итоговый stock
        total_result_stock = sum(product.get('stock', 0) for product in result_products)
        print(f"📊 Итоговый stock всех товаров: {total_result_stock}")
        print(f"📊 Ожидаемый stock: {total_positive_stock}")
        print(f"📊 Разница: {total_positive_stock - total_result_stock}")
        
        return result_products

    def _has_images(self, product: dict) -> bool:
        """Проверка наличия изображений у товара"""
        if not product.get('images'):
            return False
        
        images = product['images']
        if not isinstance(images, dict):
            return False
        
        # Проверяем size в meta
        meta = images.get('meta', {})
        return meta.get('size', 0) > 0

    async def _get_product_images(self, product: dict) -> str:
        """Получение изображений товара по отдельному API endpoint с кэшированием"""
        if not self._has_images(product):
            return None
        
        try:
            images_href = product['images']['meta']['href']
            product_name = product.get('name', 'Unknown')
            
            # Проверяем кэш изображений
            cache_key = f"{product.get('id', 'unknown')}_{images_href}"
            if self._is_image_cache_valid(cache_key):
                cached_url = self._images_cache[cache_key]['proxy_url']
                print(f"⚡ Используем кэш изображения для товара: {product_name}")
                return cached_url
            
            print(f"🖼️ Загружаем изображения для товара: {product_name}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(images_href, headers=self.headers) as response:
                    if response.status == 200:
                        images_data = await response.json()
                        
                        if images_data.get('rows'):
                            first_image = images_data['rows'][0]
                            download_href = first_image.get('meta', {}).get('downloadHref')
                            
                            if download_href:
                                image_id = download_href.split('/')[-1]
                                proxy_url = f"/proxy/image/{image_id}"
                                
                                # Кэшируем результат
                                self._images_cache[cache_key] = {
                                    'proxy_url': proxy_url,
                                    'timestamp': time.time(),
                                    'image_id': image_id
                                }
                                
                                print(f"✅ Изображение найдено и закэшировано: {proxy_url}")
                                return proxy_url
            
            print(f"⚠️ Не удалось получить изображения для товара")
            return None
            
        except Exception as e:
            print(f"⚠️ Ошибка получения изображений: {e}")
            return None

    def _determine_category_by_name(self, product_name):
        """Определение категории по названию товара"""
        name_lower = product_name.lower()
        
        # Словарь ключевых слов для категорий
        category_keywords = {
            'Джинсы': ['джинсы', 'jeans'],
            'Брюки': ['брюки', 'pants', 'trousers'],
            'Юбки': ['юбка', 'юбки', 'skirt'],
            'Платье': ['платье', 'платья', 'dress'],
            'Топы': ['топ', 'топы', 'top'],
            'Блузка': ['блузка', 'блузки', 'blouse'],
            'Рубашка': ['рубашка', 'рубашки', 'shirt'],
            'Джемпер': ['джемпер', 'джемперы', 'jumper'],
            'Свитер': ['свитер', 'свитера', 'sweater'],
            'Кардиган': ['кардиган', 'cardigan'],
            'Жакет': ['жакет', 'жакеты', 'jacket'],
            'Пиджак': ['пиджак', 'пиджаки', 'blazer'],
            'Костюм': ['костюм', 'костюмы', 'suit'],
            'Верхняя одежда': ['куртка', 'куртки', 'пальто', 'coat', 'jacket'],
            'Футболки': ['футболка', 'футболки', 't-shirt', 'tshirt'],
            'Поло': ['поло', 'polo'],
            'Худи': ['худи', 'hoodie'],
            'Свитшот': ['свитшот', 'sweatshirt'],
            'Лонгслив': ['лонгслив', 'longsleeve'],
            'Водолазки': ['водолазка', 'водолазки', 'turtleneck'],
            'Боди': ['боди', 'body'],
            'Лосины': ['лосины', 'leggings'],
            'Шорты': ['шорты', 'shorts'],
            'Комплект': ['комплект', 'комплекты', 'set'],
            'Аксессуары': ['ремень', 'ремни', 'belt', 'сумка', 'сумки', 'bag', 'шарф', 'шарфы', 'scarf'],
            'Блузон': ['блузон', 'blouson'],
            'Жилет': ['жилет', 'жилеты', 'vest']
        }
        
        # Проверяем каждую категорию
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category
        
        # Если не найдено, возвращаем "other"
        return "other"

    def _extract_modifications(self, name):
        """Извлечение модификаций (размер и цвет) из названия товара"""
        modifications = {'size': None, 'color': None}
        
        # Ищем размеры в скобках или после запятой
        size_patterns = [
            r'\((\d{2,3})\)',  # (42), (44), (46)
            r',\s*(\d{2,3})\s*\)',  # , 42), , 44)
            r'размер\s*(\d{2,3})',  # размер 42
            r'(\d{2,3})\s*размер',  # 42 размер
            r'\b(\d{2,3})\b',  # просто число 42, 44, 46
            r'\b(XS|S|M|L|XL|XXL)\b',  # буквенные размеры
            r'\b(One\s*Size|OS|one\s*size|os)\b'  # One Size
        ]
        
        # Ищем цвета
        color_patterns = [
            r'\(([^)]*?(?:белый|черный|красный|синий|зеленый|желтый|розовый|оранжевый|фиолетовый|коричневый|серый|голубой|бежевый|бордовый|хаки|шоколад|крем|молочный|ваниль|алый|лиловый|салатовый|бронзовый)[^)]*?)\)',
            r',\s*([^)]*?(?:белый|черный|красный|синий|зеленый|желтый|розовый|оранжевый|фиолетовый|коричневый|серый|голубой|бежевый|бордовый|хаки|шоколад|крем|молочный|ваниль|алый|лиловый|салатовый|бронзовый)[^)]*?)\s*\)',
            r'\b(белый|черный|красный|синий|зеленый|желтый|розовый|оранжевый|фиолетовый|коричневый|серый|голубой|бежевый|бордовый|хаки|шоколад|крем|молочный|ваниль|алый|лиловый|салатовый|бронзовый)\b',
            r'\b(White|Black|Red|Blue|Green|Yellow|Pink|Orange|Purple|Brown|Grey|Gray|Cream|Beige|Burgundy|Khaki|Chocolate|Milk|Vanilla|Scarlet|Lilac|Lime|Bronze)\b'
        ]
        
        import re
        
        # Ищем размер
        for pattern in size_patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                size = match.group(1).strip()
                # Валидация размера
                if self._is_valid_size(size):
                    modifications['size'] = size
                    break
        
        # Ищем цвет
        for pattern in color_patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                color = match.group(1).strip()
                # Валидация цвета
                if self._is_valid_color(color):
                    modifications['color'] = color
                    break
        
        return modifications

    def _is_valid_size(self, size):
        """Проверка валидности размера"""
        if not size:
            return False
        
        size_lower = size.lower()
        
        # Валидные размеры
        valid_sizes = [
            'xs', 's', 'm', 'l', 'xl', 'xxl', 'xxxl',
            'one size', 'os', 'one size',
            '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
            '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52'
        ]
        
        return size_lower in valid_sizes

    def _is_valid_color(self, color):
        """Проверка валидности цвета"""
        if not color:
            return False
        
        color_lower = color.lower()
        
        # Валидные цвета
        valid_colors = [
            'белый', 'черный', 'красный', 'синий', 'зеленый', 'желтый', 'розовый', 
            'оранжевый', 'фиолетовый', 'коричневый', 'серый', 'голубой', 'бежевый', 
            'бордовый', 'хаки', 'шоколад', 'крем', 'молочный', 'ваниль', 'алый', 
            'лиловый', 'салатовый', 'бронзовый', 'светло-серый', 'темно-серый',
            'white', 'black', 'red', 'blue', 'green', 'yellow', 'pink', 'orange', 
            'purple', 'brown', 'grey', 'gray', 'cream', 'beige', 'burgundy', 'khaki', 
            'chocolate', 'milk', 'vanilla', 'scarlet', 'lilac', 'lime', 'bronze'
        ]
        
        return color_lower in valid_colors

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

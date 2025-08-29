#!/usr/bin/env python3
"""
Справочник всех параметров, которые мы берем из МойСклад
Обновлен на основе анализа кода moysklad_api.py
"""

# 📦 ПАРАМЕТРЫ ТОВАРОВ (products)
PRODUCT_PARAMETERS = {
    # Основные поля товара
    'id': 'product.get("id") - Уникальный идентификатор товара в МойСклад',
    'name': 'product.get("name") - Название товара',
    'description': 'product.get("description") - Описание товара',
    'article': 'product.get("article") - Артикул товара',
    'pathName': 'product.get("pathName") - Путь к товару (для определения категории)',
    'productFolder': 'product.get("productFolder") - Папка товара (для определения категории)',
    'images': 'product.get("images") - Изображения товара',
    'salePrices': 'product.get("salePrices") - Цены продажи товара',
    
    # Дополнительные поля
    'meta': 'product.get("meta") - Метаданные товара',
    'code': 'product.get("code") - Код товара',
    'externalCode': 'product.get("externalCode") - Внешний код товара',
    'archived': 'product.get("archived") - Архивный статус',
    'updated': 'product.get("updated") - Дата обновления',
    'created': 'product.get("created") - Дата создания'
}

# 🔧 ПАРАМЕТРЫ МОДИФИКАЦИЙ (variants)
VARIANT_PARAMETERS = {
    # Основные поля модификации
    'id': 'variant.get("id") - Уникальный идентификатор модификации',
    'name': 'variant.get("name") - Название модификации',
    'product': 'variant.get("product") - Ссылка на родительский товар',
    'characteristics': 'variant.get("characteristics") - Характеристики модификации',
    'salePrices': 'variant.get("salePrices") - Цены продажи модификации',
    
    # Дополнительные поля
    'meta': 'variant.get("meta") - Метаданные модификации',
    'code': 'variant.get("code") - Код модификации',
    'externalCode': 'variant.get("externalCode") - Внешний код модификации',
    'archived': 'variant.get("archived") - Архивный статус',
    'updated': 'variant.get("updated") - Дата обновления',
    'created': 'variant.get("created") - Дата создания'
}

# 📊 ПАРАМЕТРЫ ОСТАТКОВ (stock)
STOCK_PARAMETERS = {
    # Основные поля остатка
    'meta': 'stock_item.get("meta") - Метаданные остатка (содержит href к товару/модификации)',
    'quantity': 'stock_item.get("quantity") - Количество товара на складе',
    'reserve': 'stock_item.get("reserve") - Зарезервированное количество',
    'inTransit': 'stock_item.get("inTransit") - Количество в пути',
    
    # Дополнительные поля
    'name': 'stock_item.get("name") - Название товара/модификации',
    'code': 'stock_item.get("code") - Код товара/модификации',
    'externalCode': 'stock_item.get("externalCode") - Внешний код'
}

# 🎨 ПАРАМЕТРЫ ХАРАКТЕРИСТИК (characteristics)
CHARACTERISTIC_PARAMETERS = {
    # Основные поля характеристики
    'name': 'char.get("name") - Название характеристики (например, "Цвет", "Размер")',
    'value': 'char.get("value") - Значение характеристики (например, "Красный", "42")',
    
    # Дополнительные поля
    'id': 'char.get("id") - Идентификатор характеристики',
    'meta': 'char.get("meta") - Метаданные характеристики'
}

# 🖼️ ПАРАМЕТРЫ ИЗОБРАЖЕНИЙ (images)
IMAGE_PARAMETERS = {
    # Основные поля изображения
    'meta': 'images.get("meta") - Метаданные изображений',
    'size': 'meta.get("size") - Размер изображения',
    'href': 'meta.get("href") - Ссылка на изображение',
    
    # Дополнительные поля
    'title': 'images.get("title") - Заголовок изображения',
    'filename': 'images.get("filename") - Имя файла изображения'
}

# 💰 ПАРАМЕТРЫ ЦЕН (salePrices)
PRICE_PARAMETERS = {
    # Основные поля цены
    'value': 'price.get("value") - Значение цены в копейках',
    'currency': 'price.get("currency") - Валюта цены',
    'priceType': 'price.get("priceType") - Тип цены',
    
    # Дополнительные поля
    'id': 'price.get("id") - Идентификатор цены',
    'meta': 'price.get("meta") - Метаданные цены'
}

# 📁 ПАРАМЕТРЫ ПАПОК (productFolder)
FOLDER_PARAMETERS = {
    # Основные поля папки
    'id': 'folder.get("id") - Идентификатор папки',
    'name': 'folder.get("name") - Название папки (используется как категория)',
    'pathName': 'folder.get("pathName") - Путь к папке',
    
    # Дополнительные поля
    'meta': 'folder.get("meta") - Метаданные папки',
    'code': 'folder.get("code") - Код папки',
    'externalCode': 'folder.get("externalCode") - Внешний код папки'
}

# 🔗 ПАРАМЕТРЫ МЕТАДАННЫХ (meta)
META_PARAMETERS = {
    # Основные поля метаданных
    'href': 'meta.get("href") - Ссылка на ресурс',
    'type': 'meta.get("type") - Тип ресурса',
    'mediaType': 'meta.get("mediaType") - Тип медиа',
    'size': 'meta.get("size") - Размер ресурса',
    
    # Дополнительные поля
    'uuidHref': 'meta.get("uuidHref") - UUID ссылка',
    'downloadHref': 'meta.get("downloadHref") - Ссылка для скачивания'
}

# 📋 ИТОГОВАЯ СТРУКТУРА ТОВАРА (result_product)
RESULT_PRODUCT_STRUCTURE = {
    # Основные поля
    'id': 'product.get("name") - ID товара (используется название)',
    'original_id': 'product_id - Оригинальный ID из МойСклад',
    'name': 'clean_name - Очищенное название товара',
    'description': 'product.get("description") - Описание товара',
    'article': 'product.get("article") - Артикул товара',
    'price': 'int(price) - Цена товара в рублях',
    'image': 'image_url или None - URL изображения',
    'stock': 'int(total_stock) - Общий остаток товара',
    'category': 'category - Категория товара',
    'modifications_text': 'f"В наличии: {total_stock}" - Текст о наличии',
    'available_colors': 'available_colors - Доступные цвета',
    'available_sizes': 'available_sizes - Доступные размеры',
    'variants': '[] - Список модификаций товара'
}

# 🔧 СТРУКТУРА МОДИФИКАЦИИ (variant_data)
VARIANT_STRUCTURE = {
    # Основные поля
    'id': 'variant_id - ID модификации',
    'name': 'variant.get("name") - Название модификации',
    'stock': 'int(variant_stock) - Остаток модификации',
    'price': 'int(price) - Цена модификации',
    'sizes': '[] - Список размеров модификации',
    'colors': '[] - Список цветов модификации'
}

def print_all_parameters():
    """Вывести все параметры, которые мы берем из МойСклад"""
    print("📦 ПАРАМЕТРЫ, КОТОРЫЕ МЫ БЕРЕМ ИЗ МОЙСКЛАД")
    print("=" * 80)
    
    print("\n🏷️ ПАРАМЕТРЫ ТОВАРОВ (products):")
    for param, description in PRODUCT_PARAMETERS.items():
        print(f"  • {param}: {description}")
    
    print("\n🔧 ПАРАМЕТРЫ МОДИФИКАЦИЙ (variants):")
    for param, description in VARIANT_PARAMETERS.items():
        print(f"  • {param}: {description}")
    
    print("\n📊 ПАРАМЕТРЫ ОСТАТКОВ (stock):")
    for param, description in STOCK_PARAMETERS.items():
        print(f"  • {param}: {description}")
    
    print("\n🎨 ПАРАМЕТРЫ ХАРАКТЕРИСТИК (characteristics):")
    for param, description in CHARACTERISTIC_PARAMETERS.items():
        print(f"  • {param}: {description}")
    
    print("\n🖼️ ПАРАМЕТРЫ ИЗОБРАЖЕНИЙ (images):")
    for param, description in IMAGE_PARAMETERS.items():
        print(f"  • {param}: {description}")
    
    print("\n💰 ПАРАМЕТРЫ ЦЕН (salePrices):")
    for param, description in PRICE_PARAMETERS.items():
        print(f"  • {param}: {description}")
    
    print("\n📁 ПАРАМЕТРЫ ПАПОК (productFolder):")
    for param, description in FOLDER_PARAMETERS.items():
        print(f"  • {param}: {description}")
    
    print("\n🔗 ПАРАМЕТРЫ МЕТАДАННЫХ (meta):")
    for param, description in META_PARAMETERS.items():
        print(f"  • {param}: {description}")
    
    print("\n📋 ИТОГОВАЯ СТРУКТУРА ТОВАРА:")
    for param, description in RESULT_PRODUCT_STRUCTURE.items():
        print(f"  • {param}: {description}")
    
    print("\n🔧 СТРУКТУРА МОДИФИКАЦИИ:")
    for param, description in VARIANT_STRUCTURE.items():
        print(f"  • {param}: {description}")
    
    print(f"\n📊 ВСЕГО ПАРАМЕТРОВ:")
    total_params = (
        len(PRODUCT_PARAMETERS) + 
        len(VARIANT_PARAMETERS) + 
        len(STOCK_PARAMETERS) + 
        len(CHARACTERISTIC_PARAMETERS) + 
        len(IMAGE_PARAMETERS) + 
        len(PRICE_PARAMETERS) + 
        len(FOLDER_PARAMETERS) + 
        len(META_PARAMETERS)
    )
    print(f"  • Всего параметров: {total_params}")
    print(f"  • Параметров товаров: {len(PRODUCT_PARAMETERS)}")
    print(f"  • Параметров модификаций: {len(VARIANT_PARAMETERS)}")
    print(f"  • Параметров остатков: {len(STOCK_PARAMETERS)}")
    print(f"  • Параметров характеристик: {len(CHARACTERISTIC_PARAMETERS)}")
    print(f"  • Параметров изображений: {len(IMAGE_PARAMETERS)}")
    print(f"  • Параметров цен: {len(PRICE_PARAMETERS)}")
    print(f"  • Параметров папок: {len(FOLDER_PARAMETERS)}")
    print(f"  • Параметров метаданных: {len(META_PARAMETERS)}")

if __name__ == "__main__":
    print_all_parameters()

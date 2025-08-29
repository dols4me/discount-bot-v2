#!/usr/bin/env python3
"""
Полный справочник всех цветов и размеров из МойСклад
Обновлен на основе анализа всех товаров
"""

# 🎨 ВСЕ ЦВЕТА (49 уникальных)
ALL_COLORS = {
    # Русские цвета
    'russian': [
        'белый', 'черный', 'красный', 'синий', 'зеленый', 'желтый', 'розовый', 
        'оранжевый', 'фиолетовый', 'коричневый', 'серый', 'голубой', 'бежевый', 
        'бордовый', 'хаки', 'шоколад', 'крем', 'молочный', 'ваниль', 'алый', 
        'лиловый', 'салатовый', 'бронзовый', 'светло-серый', 'темно-серый'
    ],
    
    # Английские цвета
    'english': [
        'white', 'black', 'red', 'blue', 'green', 'yellow', 'pink', 'orange', 
        'purple', 'brown', 'grey', 'gray', 'cream', 'beige', 'burgundy', 'khaki', 
        'chocolate', 'milk', 'vanilla', 'scarlet', 'lilac', 'lime', 'bronze'
    ],
    
    # Дополнительные варианты
    'additional': [
        'bordo', 'light-beige', 'dark-green', 'dark-denim'
    ]
}

# 📏 ВСЕ РАЗМЕРЫ (27 уникальных)
ALL_SIZES = {
    # Числовые размеры (женские)
    'numeric': [
        '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
        '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52'
    ],
    
    # Буквенные размеры
    'letter': [
        'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'
    ],
    
    # Универсальные размеры
    'universal': [
        'One Size', 'OS', 'one size', 'os'
    ]
}

# 🔗 НОРМАЛИЗАЦИЯ ЦВЕТОВ (приведение к единому виду)
COLOR_NORMALIZATION = {
    # Русские -> Английские
    'белый': 'white',
    'черный': 'black',
    'красный': 'red',
    'синий': 'blue',
    'зеленый': 'green',
    'желтый': 'yellow',
    'розовый': 'pink',
    'оранжевый': 'orange',
    'фиолетовый': 'purple',
    'коричневый': 'brown',
    'серый': 'grey',
    'голубой': 'blue',
    'бежевый': 'beige',
    'бордовый': 'burgundy',
    'хаки': 'khaki',
    'шоколад': 'chocolate',
    'крем': 'cream',
    'молочный': 'milk',
    'ваниль': 'vanilla',
    'алый': 'scarlet',
    'лиловый': 'lilac',
    'салатовый': 'lime',
    'бронзовый': 'bronze',
    'светло-серый': 'light-grey',
    'темно-серый': 'dark-grey',
    
    # Английские -> Английские (нормализация)
    'white': 'white',
    'black': 'black',
    'red': 'red',
    'blue': 'blue',
    'green': 'green',
    'yellow': 'yellow',
    'pink': 'pink',
    'orange': 'orange',
    'purple': 'purple',
    'brown': 'brown',
    'grey': 'grey',
    'gray': 'grey',
    'cream': 'cream',
    'beige': 'beige',
    'burgundy': 'burgundy',
    'khaki': 'khaki',
    'chocolate': 'chocolate',
    'milk': 'milk',
    'vanilla': 'vanilla',
    'scarlet': 'scarlet',
    'lilac': 'lilac',
    'lime': 'lime',
    'bronze': 'bronze',
    
    # Дополнительные
    'bordo': 'burgundy',
    'light-beige': 'light-beige',
    'dark-green': 'dark-green',
    'dark-denim': 'dark-denim'
}

# 📏 НОРМАЛИЗАЦИЯ РАЗМЕРОВ (приведение к единому виду)
SIZE_NORMALIZATION = {
    # Числовые -> Числовые
    '28': '28', '29': '29', '30': '30', '31': '31', '32': '32', '33': '33',
    '34': '34', '35': '35', '36': '36', '37': '37', '38': '38', '39': '39',
    '40': '40', '41': '41', '42': '42', '43': '43', '44': '44', '45': '45',
    '46': '46', '47': '47', '48': '48', '49': '49', '50': '50', '51': '51', '52': '52',
    
    # Буквенные -> Буквенные (нормализация)
    'XS': 'XS', 'S': 'S', 'M': 'M', 'L': 'L', 'XL': 'XL', 'XXL': 'XXL', 'XXXL': 'XXXL',
    'xs': 'XS', 's': 'S', 'm': 'M', 'l': 'L', 'xl': 'XL', 'xxl': 'XXL', 'xxxl': 'XXXL',
    
    # Универсальные -> Универсальные (нормализация)
    'One Size': 'One Size', 'OS': 'One Size', 'one size': 'One Size', 'os': 'One Size',
    'One size': 'One Size'
}

def get_all_colors():
    """Получить все цвета в виде плоского списка"""
    all_colors = []
    for category in ALL_COLORS.values():
        all_colors.extend(category)
    return sorted(list(set(all_colors)))

def get_all_sizes():
    """Получить все размеры в виде плоского списка"""
    all_sizes = []
    for category in ALL_SIZES.values():
        all_sizes.extend(category)
    return sorted(list(set(all_sizes)))

def normalize_color(color):
    """Нормализовать цвет (привести к единому виду)"""
    if not color:
        return None
    
    color_lower = color.lower()
    return COLOR_NORMALIZATION.get(color_lower, color_lower)

def normalize_size(size):
    """Нормализовать размер (привести к единому виду)"""
    if not size:
        return None
    
    size_lower = size.lower()
    return SIZE_NORMALIZATION.get(size_lower, size_lower)

def is_valid_color(color):
    """Проверить, является ли цвет валидным"""
    if not color:
        return False
    
    all_colors = get_all_colors()
    return color.lower() in [c.lower() for c in all_colors]

def is_valid_size(size):
    """Проверить, является ли размер валидным"""
    if not size:
        return False
    
    all_sizes = get_all_sizes()
    return size.lower() in [s.lower() for s in all_sizes]

if __name__ == "__main__":
    print("🎨 СПРАВОЧНИК ЦВЕТОВ И РАЗМЕРОВ ИЗ МОЙСКЛАД")
    print("=" * 60)
    
    print(f"\n📊 Всего уникальных цветов: {len(get_all_colors())}")
    print(f"📊 Всего уникальных размеров: {len(get_all_sizes())}")
    
    print(f"\n🎨 ВСЕ ЦВЕТА:")
    for i, color in enumerate(get_all_colors(), 1):
        normalized = normalize_color(color)
        print(f"  {i:2d}. '{color}' -> '{normalized}'")
    
    print(f"\n📏 ВСЕ РАЗМЕРЫ:")
    for i, size in enumerate(get_all_sizes(), 1):
        normalized = normalize_size(size)
        print(f"  {i:2d}. '{size}' -> '{normalized}'")
    
    print(f"\n✅ Справочник готов к использованию!")

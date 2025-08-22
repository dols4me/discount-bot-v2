#!/usr/bin/env python3
import sys
sys.path.append('.')

from moysklad_api import MoySkladAPI

def test_simple_parsing():
    """Тестируем парсер без API"""
    
    api = MoySkladAPI()
    
    # Тестовые названия
    test_names = [
        "Платье Aurana в клетку Берберри р.46",
        "Платье Sabrina Scala (48, Светло-Серый)",
        "Блуза принт горох/сердце из вискозы Stocman р.54",
        "Жилет пиджачного кроя",
        "Топ на завязках BELUCCI (M, Black)",
        "Платье One Size",
        "Блуза OS",
        "Жилет (OneSize, Черный)",
        "Топ (OS, White)"
    ]
    
    print("🔍 Тестируем парсер модификаций:\n")
    
    for name in test_names:
        print(f"📦 Исходное название: {name}")
        
        # Проверяем наличие скобок
        import re
        has_brackets = bool(re.search(r'\([^)]+\)', name))
        print(f"   Скобки с модификациями: {'✅ Есть' if has_brackets else '❌ Нет'}")
        
        # Извлекаем базовое название
        base_name = api._extract_base_name(name)
        print(f"   Базовое название: {base_name}")
        
        # Извлекаем модификации
        modifications = api._extract_modifications(name)
        print(f"   Модификации: {modifications}")
        
        print()

if __name__ == "__main__":
    test_simple_parsing()

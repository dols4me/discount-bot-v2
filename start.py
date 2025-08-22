#!/usr/bin/env python3
"""
Простой скрипт для запуска Telegram Shop Bot
"""

import os
import sys
import socket

def find_free_port(start_port=8000, max_attempts=100):
    """Находит свободный порт начиная с start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    print("🚀 Telegram Shop Bot")
    print("=" * 30)
    
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("⚠️  Файл .env не найден!")
        print("📝 Создайте .env файл на основе env_example.txt")
        print("🔑 Добавьте необходимые токены")
        return
    
    print("✅ Конфигурация найдена")
    print("\nВыберите режим запуска:")
    print("1. 🤖 Только Telegram бот")
    print("2. 🌐 Только веб-приложение")
    print("3. 🚀 Бот + веб-приложение")
    print("4. ❌ Выход")
    
    while True:
        try:
            choice = input("\nВведите номер (1-4): ").strip()
            
            if choice == '1':
                print("\n🤖 Запуск Telegram бота...")
                os.system('python3 bot.py')
                break
            elif choice == '2':
                print("\n🌐 Запуск веб-приложения...")
                port = find_free_port(8000)
                if port:
                    print(f"📱 Откройте http://localhost:{port} в браузере")
                    os.system(f'python3 -c "import uvicorn; from webapp import app; uvicorn.run(app, host=\'0.0.0.0\', port={port})"')
                else:
                    print("❌ Не удалось найти свободный порт")
                break
            elif choice == '3':
                print("\n🚀 Запуск полного приложения...")
                os.system('python3 run_full.py')
                break
            elif choice == '4':
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор. Введите число от 1 до 4.")
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()

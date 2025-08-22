#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота и веб-приложения одновременно
"""

import asyncio
import threading
import uvicorn
from bot import ShopBot

def run_webapp():
    """Запуск веб-приложения"""
    uvicorn.run("webapp:app", host="0.0.0.0", port=8000, reload=False)

def run_bot():
    """Запуск Telegram бота"""
    bot = ShopBot()
    bot.run()

if __name__ == "__main__":
    print("🚀 Запуск полного приложения...")
    print("🌐 Веб-приложение будет доступно на http://localhost:8000")
    print("🤖 Telegram бот запускается...")
    
    # Запускаем веб-приложение в отдельном потоке
    webapp_thread = threading.Thread(target=run_webapp, daemon=True)
    webapp_thread.start()
    
    print("✅ Веб-приложение запущено")
    
    # Даем время веб-приложению запуститься
    import time
    time.sleep(2)
    
    # Запускаем бота в основном потоке
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 Остановка приложения...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

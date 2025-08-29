import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# МойСклад API Configuration
MOYSKLAD_API_TOKEN = "70ff03c8f6f33ae7b62744eb0af127b043de02fb"  # API токен для Bearer аутентификации
MOYSKLAD_BASE_URL = "https://api.moysklad.ru/api/remap/1.2"

# MoySklad Basic Auth (для получения нового токена)
MOYSKLAD_LOGIN = "admin@w4store"  # Логин от МойСклад
MOYSKLAD_PASSWORD = "Zxcx12321!!"  # Пароль от МойСклад

# Web App Configuration
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://your-webapp-url.com')  # URL вашего веб-приложения

# Database Configuration
DATABASE_PATH = "shop.db"

# Shop Configuration
SHOP_NAME = "W4STORE - WOMEN'S CLOTHING"
SHOP_DESCRIPTION = "Интернет-магазин женской одежды в Telegram с интеграцией МойСклад"
CURRENCY = "₽"

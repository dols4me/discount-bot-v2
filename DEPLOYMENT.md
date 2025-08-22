# Инструкции по развертыванию

## 🚀 Быстрый запуск

### 1. Активация виртуального окружения
```bash
source .venv/bin/activate
```

### 2. Запуск сервера
```bash
python3 webapp.py
```

### 3. Проверка работы
Откройте в браузере: http://localhost:8000/

## 📋 Требования

### Python 3.8+
```bash
python3 --version
```

### Зависимости
```bash
pip install fastapi uvicorn aiohttp jinja2
```

### MoySklad API
- API токен должен быть настроен в `moysklad_api.py`
- Проверьте переменную `api_token` в классе `MoySkladAPI`

## 🔧 Конфигурация

### Порт сервера
По умолчанию: 8000
Изменить в `webapp.py`:
```python
uvicorn.run("webapp:app", host="0.0.0.0", port=8000, reload=True)
```

### Настройки MoySklad
В `moysklad_api.py`:
```python
self.base_url = "https://api.moysklad.ru/api/remap/1.2"
self.api_token = "ваш_токен"
```

## 📁 Структура проекта

```
discount_bot/
├── webapp.py              # Основной сервер
├── moysklad_api.py        # API MoySklad
├── database.py            # База данных
├── config.py              # Конфигурация
├── templates/             # HTML шаблоны
├── static/                # Статические файлы
├── VERSION_INFO.md        # Описание версии
└── DEPLOYMENT.md          # Этот файл
```

## 🐛 Устранение неполадок

### Порт занят
```bash
pkill -f "python3 webapp.py"
# или
lsof -ti:8000 | xargs kill -9
```

### Проблемы с MoySklad
- Проверьте API токен
- Проверьте доступность API
- Проверьте лимиты запросов

### Проблемы с изображениями
- Проверьте endpoint `/proxy/image/{image_id}`
- Проверьте авторизацию MoySklad
- Проверьте логи сервера

## 📊 Мониторинг

### Логи сервера
Сервер выводит подробные логи в консоль:
- Загрузка товаров
- Кэширование
- Обработка изображений
- API запросы

### Проверка здоровья
```bash
curl http://localhost:8000/api/products?limit=1
curl http://localhost:8000/api/categories
```

## 🔄 Обновление

### Остановка сервера
```bash
pkill -f "python3 webapp.py"
```

### Обновление кода
```bash
git pull origin main
# или скопировать новые файлы
```

### Перезапуск
```bash
source .venv/bin/activate
python3 webapp.py
```

## 📝 Примечания

- Сервер автоматически перезагружается при изменении файлов
- Кэш товаров обновляется каждые 5 минут
- Изображения кэшируются на 1 час
- Все API endpoints документированы в FastAPI

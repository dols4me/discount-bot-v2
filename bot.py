import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, WebAppInfo, MenuButton, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import TELEGRAM_BOT_TOKEN, SHOP_NAME, SHOP_DESCRIPTION, CURRENCY, WEBAPP_URL
from database import Database
from moysklad_api import MoySkladAPI
from keyboards import Keyboards

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ShopBot:
    def __init__(self):
        self.db = Database()
        self.moysklad = MoySkladAPI()
        self.user_states = {}  # Состояния пользователей для multi-step процессов
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Добавляем пользователя в базу
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Настраиваем Menu Button для Web App
        if WEBAPP_URL != 'https://your-webapp-url.com':
            try:
                await context.bot.set_chat_menu_button(
                    chat_id=chat_id,
                    menu_button=MenuButtonWebApp(
                        text="🛍️ Магазин",
                        web_app=WebAppInfo(url=WEBAPP_URL)
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to set menu button: {e}")
        
        welcome_text = f"""
🎉 Добро пожаловать в {SHOP_NAME}!

{SHOP_DESCRIPTION}

🌐 Нажмите кнопку "Открыть магазин" для перехода в веб-каталог
📱 Или используйте кнопки меню для быстрого доступа

Выберите действие:
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=Keyboards.get_main_menu()
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback-запросов от inline-кнопок"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "main_menu":
            await self.show_main_menu(query)
        elif data == "catalog":
            await self.show_catalog(query)
        elif data == "cart":
            await self.show_cart(query)
        elif data == "orders":
            await self.show_orders(query)
        elif data == "about":
            await self.show_about(query)
        elif data == "support":
            await self.show_support(query)
        elif data.startswith("product_"):
            product_id = data.split("_")[1]
            await self.show_product(query, product_id)
        elif data.startswith("add_"):
            product_id = data.split("_")[1]
            await self.add_to_cart(query, product_id, 1)
        elif data.startswith("qty_"):
            parts = data.split("_")
            product_id = parts[1]
            quantity = int(parts[2])
            await self.add_to_cart(query, product_id, quantity)
        elif data == "checkout":
            await self.show_checkout(query)
        elif data == "confirm_order":
            await self.confirm_order(query)
        elif data == "clear_cart":
            await self.clear_cart(query)
        elif data.startswith("page_"):
            await self.show_catalog_page(query, data)
    
    async def show_main_menu(self, query):
        """Показать главное меню"""
        await query.edit_message_text(
            f"🏠 Главное меню {SHOP_NAME}",
            reply_markup=Keyboards.get_main_menu()
        )
    
    async def show_catalog(self, query):
        """Показать каталог товаров"""
        products = await self.moysklad.get_products(limit=5)
        
        if not products:
            await query.edit_message_text(
                "😔 К сожалению, товары временно недоступны",
                reply_markup=Keyboards.get_main_menu()
            )
            return
        
        catalog_text = "🛍️ Каталог товаров:\n\n"
        for i, product in enumerate(products[:5], 1):
            catalog_text += f"{i}. {product['name']}\n"
            catalog_text += f"   💰 {product['price']} {CURRENCY}\n"
            catalog_text += f"   📦 В наличии: {product['stock']} шт.\n\n"
        
        catalog_text += "Выберите товар для просмотра:"
        
        # Создаем клавиатуру с товарами
        keyboard = []
        for product in products[:5]:
            keyboard.append([InlineKeyboardButton(
                product['name'], 
                callback_data=f"product_{product['id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
        
        await query.edit_message_text(
            catalog_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def show_product(self, query, product_id):
        """Показать информацию о товаре"""
        product = await self.moysklad.get_product_by_id(product_id)
        
        if not product:
            await query.edit_message_text(
                "😔 Товар не найден",
                reply_markup=Keyboards.get_main_menu()
            )
            return
        
        # Проверяем, есть ли товар в корзине
        cart_items = self.db.get_cart(query.from_user.id)
        in_cart = any(item['product_id'] == product_id for item in cart_items)
        
        product_text = f"""
🛍️ {product['name']}

📝 {product['description']}

💰 Цена: {product['price']} {CURRENCY}
📦 В наличии: {product['stock']} шт.
        """
        
        await query.edit_message_text(
            product_text,
            reply_markup=Keyboards.get_product_keyboard(product_id, in_cart)
        )
    
    async def add_to_cart(self, query, product_id, quantity):
        """Добавить товар в корзину"""
        product = await self.moysklad.get_product_by_id(product_id)
        
        if not product:
            await query.answer("Товар не найден!")
            return
        
        if product['stock'] < quantity:
            await query.answer(f"Недостаточно товара на складе! Доступно: {product['stock']}")
            return
        
        # Добавляем в корзину
        self.db.add_to_cart(
            user_id=query.from_user.id,
            product_id=product_id,
            product_name=product['name'],
            quantity=quantity,
            price=product['price']
        )
        
        await query.answer(f"✅ {product['name']} добавлен в корзину!")
        
        # Показываем обновленную информацию о товаре
        await self.show_product(query, product_id)
    
    async def show_cart(self, query):
        """Показать корзину пользователя"""
        cart_items = self.db.get_cart(query.from_user.id)
        
        if not cart_items:
            await query.edit_message_text(
                "🛒 Ваша корзина пуста",
                reply_markup=Keyboards.get_main_menu()
            )
            return
        
        cart_text = "🛒 Ваша корзина:\n\n"
        total = 0
        
        for item in cart_items:
            item_total = item['price'] * item['quantity']
            total += item_total
            cart_text += f"📦 {item['name']}\n"
            cart_text += f"   Количество: {item['quantity']}\n"
            cart_text += f"   Цена: {item['price']} {CURRENCY}\n"
            cart_text += f"   Сумма: {item_total} {CURRENCY}\n\n"
        
        cart_text += f"💰 Итого: {total} {CURRENCY}"
        
        await query.edit_message_text(
            cart_text,
            reply_markup=Keyboards.get_cart_keyboard()
        )
    
    async def show_checkout(self, query):
        """Показать форму оформления заказа"""
        cart_items = self.db.get_cart(query.from_user.id)
        
        if not cart_items:
            await query.answer("Корзина пуста!")
            return
        
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        
        checkout_text = f"""
💳 Оформление заказа

📋 Товары в заказе:
"""
        
        for item in cart_items:
            checkout_text += f"• {item['name']} x{item['quantity']} = {item['price'] * item['quantity']} {CURRENCY}\n"
        
        checkout_text += f"\n💰 Итого: {total} {CURRENCY}\n\n"
        checkout_text += "Для оформления заказа укажите контактную информацию:"
        
        await query.edit_message_text(
            checkout_text,
            reply_markup=Keyboards.get_checkout_keyboard()
        )
    
    async def confirm_order(self, query):
        """Подтверждение заказа"""
        user_id = query.from_user.id
        cart_items = self.db.get_cart(user_id)
        
        if not cart_items:
            await query.answer("Корзина пуста!")
            return
        
        # Получаем информацию о пользователе
        user_info = self.db.get_user_info(user_id)
        
        if not user_info or not user_info.get('phone') or not user_info.get('address'):
            await query.answer("Сначала укажите телефон и адрес!")
            return
        
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        order_number = f"ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        # Создаем заказ в базе данных
        order_id = self.db.create_order(
            user_id=user_id,
            order_number=order_number,
            total_amount=total,
            items=cart_items,
            phone=user_info['phone'],
            address=user_info['address']
        )
        
        # Пытаемся создать заказ в МойСклад
        if order_id:
            moysklad_order_id = await self.moysklad.create_order({
                'order_number': order_number,
                'items': cart_items
            })
            
            if moysklad_order_id:
                # Обновляем статус заказа
                self.db.update_order_status(order_id, 'synced_with_moysklad')
        
        # Очищаем корзину
        self.db.clear_cart(user_id)
        
        success_text = f"""
✅ Заказ успешно оформлен!

📋 Номер заказа: {order_number}
💰 Сумма: {total} {CURRENCY}
📱 Телефон: {user_info['phone']}
📍 Адрес: {user_info['address']}

Мы свяжемся с вами для подтверждения заказа!
        """
        
        await query.edit_message_text(
            success_text,
            reply_markup=Keyboards.get_main_menu()
        )
    
    async def clear_cart(self, query):
        """Очистить корзину"""
        self.db.clear_cart(query.from_user.id)
        await query.answer("Корзина очищена!")
        await self.show_cart(query)
    
    async def show_orders(self, query):
        """Показать заказы пользователя"""
        user_id = query.from_user.id
        orders = self.db.get_user_orders(user_id)
        
        if not orders:
            await query.edit_message_text(
                "📋 У вас пока нет заказов",
                reply_markup=Keyboards.get_main_menu()
            )
            return
        
        orders_text = "📋 Ваши заказы:\n\n"
        
        for order in orders:
            status_emoji = {
                'new': '🆕',
                'confirmed': '✅',
                'processing': '⚙️',
                'shipped': '🚚',
                'delivered': '📦',
                'cancelled': '❌'
            }.get(order['status'], '❓')
            
            orders_text += f"{status_emoji} Заказ {order['order_number']}\n"
            orders_text += f"   Статус: {order['status']}\n"
            orders_text += f"   Сумма: {order['total_amount']} {CURRENCY}\n"
            orders_text += f"   Дата: {order['created_at']}\n\n"
        
        await query.edit_message_text(
            orders_text,
            reply_markup=Keyboards.get_main_menu()
        )
    
    async def show_about(self, query):
        """Показать информацию о магазине"""
        about_text = f"""
ℹ️ О магазине

{SHOP_NAME}

{SHOP_DESCRIPTION}

✨ Особенности:
• Широкий ассортимент товаров
• Быстрая доставка
• Качественное обслуживание
• Интеграция с системой учета

📞 Контакты:
• Телефон: +7 (XXX) XXX-XX-XX
• Email: info@shop.ru
• Адрес: г. Москва, ул. Примерная, д. 1
        """
        
        await query.edit_message_text(
            about_text,
            reply_markup=Keyboards.get_main_menu()
        )
    
    async def show_support(self, query):
        """Показать информацию о поддержке"""
        support_text = """
📞 Служба поддержки

Наши специалисты готовы помочь вам с любыми вопросами!

🕐 Время работы:
• Пн-Пт: 9:00 - 18:00
• Сб: 10:00 - 16:00
• Вс: выходной

📱 Контакты:
• Телефон: +7 (XXX) XXX-XX-XX
• WhatsApp: +7 (XXX) XXX-XX-XX
• Email: support@shop.ru
        """
        
        await query.edit_message_text(
            support_text,
            reply_markup=Keyboards.get_support_keyboard()
        )
    
    async def show_catalog_page(self, query, data):
        """Показать страницу каталога с пагинацией"""
        # Простая реализация пагинации
        await self.show_catalog(query)
    
    def run(self):
        """Запуск бота"""
        if not TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN не настроен!")
            return
        
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Запускаем бота
        logger.info("Бот запущен!")
        application.run_polling()

if __name__ == "__main__":
    bot = ShopBot()
    bot.run()

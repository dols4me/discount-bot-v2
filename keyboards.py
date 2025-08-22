from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from config import CURRENCY, WEBAPP_URL

class Keyboards:
    @staticmethod
    def get_main_menu():
        """Главное меню"""
        keyboard = [
            [InlineKeyboardButton("🌐 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("🛍️ Каталог товаров", callback_data="catalog")],
            [InlineKeyboardButton("🛒 Корзина", callback_data="cart")],
            [InlineKeyboardButton("📋 Мои заказы", callback_data="orders")],
            [InlineKeyboardButton("ℹ️ О магазине", callback_data="about")],
            [InlineKeyboardButton("📞 Поддержка", callback_data="support")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_catalog_menu():
        """Меню каталога"""
        keyboard = [
            [InlineKeyboardButton("📱 Электроника", callback_data="category_electronics")],
            [InlineKeyboardButton("👕 Одежда", callback_data="category_clothing")],
            [InlineKeyboardButton("🏠 Дом и сад", callback_data="category_home")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_product_keyboard(product_id, in_cart=False):
        """Клавиатура для товара"""
        if in_cart:
            keyboard = [
                [
                    InlineKeyboardButton("➖", callback_data=f"decrease_{product_id}"),
                    InlineKeyboardButton("➕", callback_data=f"increase_{product_id}")
                ],
                [InlineKeyboardButton("🗑️ Убрать из корзины", callback_data=f"remove_{product_id}")],
                [InlineKeyboardButton("🔙 Назад к каталогу", callback_data="catalog")]
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton("➖", callback_data=f"decrease_{product_id}"),
                    InlineKeyboardButton("1", callback_data="quantity_1"),
                    InlineKeyboardButton("➕", callback_data=f"increase_{product_id}")
                ],
                [InlineKeyboardButton("🛒 Добавить в корзину", callback_data=f"add_{product_id}")],
                [InlineKeyboardButton("🔙 Назад к каталогу", callback_data="catalog")]
            ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_cart_keyboard():
        """Клавиатура корзины"""
        keyboard = [
            [InlineKeyboardButton("💳 Оформить заказ", callback_data="checkout")],
            [InlineKeyboardButton("🗑️ Очистить корзину", callback_data="clear_cart")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_checkout_keyboard():
        """Клавиатура оформления заказа"""
        keyboard = [
            [InlineKeyboardButton("📱 Указать телефон", callback_data="set_phone")],
            [InlineKeyboardButton("📍 Указать адрес", callback_data="set_address")],
            [InlineKeyboardButton("✅ Подтвердить заказ", callback_data="confirm_order")],
            [InlineKeyboardButton("🔙 Назад к корзине", callback_data="cart")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_quantity_keyboard(product_id):
        """Клавиатура выбора количества"""
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data=f"qty_{product_id}_1"),
                InlineKeyboardButton("2", callback_data=f"qty_{product_id}_2"),
                InlineKeyboardButton("3", callback_data=f"qty_{product_id}_3")
            ],
            [
                InlineKeyboardButton("5", callback_data=f"qty_{product_id}_5"),
                InlineKeyboardButton("10", callback_data=f"qty_{product_id}_10")
            ],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"product_{product_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_pagination_keyboard(page, total_pages, category=None):
        """Клавиатура пагинации"""
        keyboard = []
        
        # Кнопки навигации
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"page_{category}_{page-1}" if category else f"page_{page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="current_page"))
        
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"page_{category}_{page+1}" if category else f"page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Кнопка возврата
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="catalog")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_order_status_keyboard(order_number):
        """Клавиатура для заказа"""
        keyboard = [
            [InlineKeyboardButton("📋 Детали заказа", callback_data=f"order_details_{order_number}")],
            [InlineKeyboardButton("🔙 Назад к заказам", callback_data="orders")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_support_keyboard():
        """Клавиатура поддержки"""
        keyboard = [
            [InlineKeyboardButton("📞 Позвонить", callback_data="call_support")],
            [InlineKeyboardButton("✉️ Написать", callback_data="write_support")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

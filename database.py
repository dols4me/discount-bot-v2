import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица корзины
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                product_id TEXT,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                size TEXT,
                image TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем новые колонки, если их нет
        try:
            cursor.execute('ALTER TABLE cart ADD COLUMN size TEXT')
        except:
            pass  # Колонка уже существует
        
        try:
            cursor.execute('ALTER TABLE cart ADD COLUMN image TEXT')
        except:
            pass  # Колонка уже существует
        
        try:
            cursor.execute('ALTER TABLE cart ADD COLUMN color TEXT')
        except:
            pass  # Колонка уже существует
        
        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                order_number TEXT UNIQUE,
                status TEXT DEFAULT 'new',
                total_amount REAL,
                items TEXT,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, first_name, last_name):
        """Добавление нового пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    def update_user_contact(self, user_id, phone, address):
        """Обновление контактной информации пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET phone = ?, address = ? WHERE user_id = ?
        ''', (phone, address, user_id))
        
        conn.commit()
        conn.close()
    
    def add_to_cart(self, user_id, product_id, product_name, quantity, price, size=None, color=None, image=None):
        """Добавление товара в корзину"""
        # Отладочная информация
        print(f"🗄️ База данных: добавление в корзину: user_id={user_id}, product_id={product_id}, quantity={quantity}, price={price}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже такой товар в корзине
        cursor.execute('''
            SELECT id, quantity FROM cart 
            WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id))
        
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Обновляем количество
            new_quantity = existing_item[1] + quantity
            print(f"🔄 Обновляем существующий товар: старый quantity={existing_item[1]}, новый quantity={new_quantity}")
            cursor.execute('''
                UPDATE cart SET quantity = ? WHERE id = ?
            ''', (new_quantity, existing_item[0]))
        else:
            # Добавляем новый товар
            print(f"➕ Добавляем новый товар: quantity={quantity}")
            cursor.execute('''
                INSERT INTO cart (user_id, product_id, product_name, quantity, price, size, color, image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, product_id, product_name, quantity, price, size, color, image))
        
        conn.commit()
        conn.close()
    
    def get_cart_item(self, user_id, product_id):
        """Получение конкретного товара из корзины"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, product_id, product_name, quantity, price FROM cart
            WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'product_id': row[1],
                'name': row[2],
                'quantity': row[3],
                'price': row[4],
            }
        return None
    
    def set_cart_quantity(self, user_id, product_id, new_quantity):
        """Установить количество товара в корзине (0 удаляет)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if new_quantity <= 0:
            cursor.execute('DELETE FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
        else:
            cursor.execute('''
                UPDATE cart SET quantity = ?
                WHERE user_id = ? AND product_id = ?
            ''', (new_quantity, user_id, product_id))
        conn.commit()
        conn.close()
    
    def remove_from_cart(self, user_id, product_id):
        """Удалить позицию из корзины"""
        print(f"🗑️ Database.remove_from_cart: user_id={user_id}, product_id={product_id}")
        print(f"🗑️ Типы данных: user_id={type(user_id)}, product_id={type(product_id)}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли товар в корзине
        cursor.execute('SELECT COUNT(*) FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
        count_before = cursor.fetchone()[0]
        print(f"🗑️ Товаров в корзине до удаления: {count_before}")
        
        # Удаляем товар
        cursor.execute('DELETE FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
        deleted_rows = cursor.rowcount
        print(f"🗑️ Удалено строк: {deleted_rows}")
        
        conn.commit()
        conn.close()
        
        print(f"🗑️ Database.remove_from_cart завершено")
    
    def get_cart(self, user_id):
        """Получение корзины пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_id, product_name, quantity, price, size, color, image 
            FROM cart WHERE user_id = ?
        ''', (user_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        return [{'product_id': item[0], 'name': item[1], 'quantity': item[2], 'price': item[3], 'size': item[4], 'color': item[5], 'image': item[6]} for item in items]
    
    def clear_cart(self, user_id):
        """Очистка корзины пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def create_order(self, user_id, order_number, total_amount, items, phone, address):
        """Создание нового заказа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (user_id, order_number, total_amount, items, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, order_number, total_amount, json.dumps(items), phone, address))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return order_id
    
    def get_user_orders(self, user_id):
        """Получение заказов пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT order_number, status, total_amount, created_at 
            FROM orders WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        orders = cursor.fetchall()
        conn.close()
        
        return [{'order_number': order[0], 'status': order[1], 'total_amount': order[2], 'created_at': order[3]} for order in orders]
    
    def get_user_info(self, user_id):
        """Получение информации о пользователе"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT phone, address FROM users WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {'phone': result[0], 'address': result[1]}
        return None
    
    def update_order_status(self, order_id, status):
        """Обновление статуса заказа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE orders SET status = ? WHERE id = ?
        ''', (status, order_id))
        
        conn.commit()
        conn.close()

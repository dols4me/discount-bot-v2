// Глобальные переменные
let currentUserId = 'demo_user';
let cartItems = [];

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    initTelegramWebApp();
    initLocalCart();
    updateCartCount();
});

// Инициализация Telegram WebApp
function initTelegramWebApp() {
    if (window.Telegram && window.Telegram.WebApp) {
        const tg = window.Telegram.WebApp;
        
        // Готовность приложения
        tg.ready();
        tg.expand();
        
        // Получаем данные пользователя
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            currentUserId = tg.initDataUnsafe.user.id;
        }
        
        // Настраиваем тему
        document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
        document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
        document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
        document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#3390ec');
        document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
        document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f5f5f5');
        document.documentElement.style.setProperty('--tg-theme-section-separator-color', tg.themeParams.section_separator_color || '#e5e5e5');
        
        console.log('Telegram WebApp initialized for user:', currentUserId);
    }
}

// Фильтрация товаров
function filterProducts() {
    const searchInput = document.getElementById('search-input');
    const clearButton = document.getElementById('clear-search');
    const searchTerm = searchInput.value.toLowerCase();
    const productCards = document.querySelectorAll('.product-card');
    const emptyState = document.getElementById('empty-catalog');
    let visibleProducts = 0;
    
    // Показываем/скрываем кнопку очистки
    if (searchTerm.length > 0) {
        clearButton.style.display = 'block';
    } else {
        clearButton.style.display = 'none';
    }
    
    productCards.forEach(card => {
        const productName = card.querySelector('.product-name').textContent.toLowerCase();
        const productSizes = card.querySelector('.product-sizes')?.textContent.toLowerCase() || '';
        const productColors = card.querySelector('.product-colors')?.textContent.toLowerCase() || '';
        const productPrice = card.querySelector('.product-price').textContent.toLowerCase();
        const productArticle = card.querySelector('.product-article')?.textContent.toLowerCase() || '';
        
        // Поиск по названию, цвету, цене, артикулу и категории
        const productId = card.getAttribute('data-product-id') || '';
        const productCategory = card.getAttribute('data-category') || '';
        
        if (productName.includes(searchTerm) || 
            productSizes.includes(searchTerm) || 
            productColors.includes(searchTerm) ||
            productPrice.includes(searchTerm) ||
            productArticle.includes(searchTerm) ||
            productId.includes(searchTerm) ||
            productCategory.includes(searchTerm)) {
            card.style.display = 'block';
            visibleProducts++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Показываем/скрываем сообщение о пустом результате
    if (visibleProducts === 0 && searchTerm.length > 0) {
        emptyState.style.display = 'block';
    } else {
        emptyState.style.display = 'none';
    }
    
    // Обновляем счетчик найденных товаров
    updateProductCounter(visibleProducts);
}

// Очистка поиска
function clearSearch() {
    const searchInput = document.getElementById('search-input');
    const clearButton = document.getElementById('clear-search');
    
    searchInput.value = '';
    clearButton.style.display = 'none';
    
    // Показываем все товары
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.style.display = 'block';
    });
    
    // Скрываем сообщение о пустом результате
    const emptyState = document.getElementById('empty-catalog');
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    // Обновляем счетчик
    updateProductCounter(productCards.length);
}

// Обновление счетчика товаров
function updateProductCounter(count) {
    const sectionTitle = document.querySelector('.section-title');
    if (sectionTitle) {
        const searchInput = document.getElementById('search-input');
        const searchTerm = searchInput.value.trim();
        
        if (searchTerm.length > 0) {
            sectionTitle.textContent = `🔍 Результаты поиска "${searchTerm}"`;
        } else {
            sectionTitle.textContent = '🛒 Все товары';
        }
    }
}

// Фильтрация по категориям
function filterByCategory(category) {
    console.log('Фильтрация по категории:', category);
    
    // Убираем активный класс со всех кнопок категорий
    document.querySelectorAll('.category-chip').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Добавляем активный класс к выбранной категории
    event.target.classList.add('active');
    
    const productsGrid = document.getElementById('products-grid');
    const productCards = productsGrid.querySelectorAll('.product-card');
    
    console.log('Всего товаров на странице:', productCards.length);
    
    let visibleCount = 0;
    
    productCards.forEach(card => {
        const productCategory = card.getAttribute('data-category');
        console.log('Товар:', card.querySelector('.product-name')?.textContent, 'Категория:', productCategory);
        
        if (category === 'all' || productCategory === category) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    console.log(`Показано товаров в категории "${category}": ${visibleCount}`);
    
    // Обновляем заголовок
    const sectionTitle = document.querySelector('.section-title');
    if (sectionTitle) {
        if (category === 'all') {
            sectionTitle.textContent = '🛒 Все товары';
        } else {
            sectionTitle.textContent = category;
        }
    }
}

// Просмотр товара
function viewProduct(productId) {
    if (window.Telegram && window.Telegram.WebApp) {
        // В Telegram WebApp можем открыть новую страницу
        window.location.href = `/product/${productId}`;
    } else {
        // В браузере открываем в новой вкладке
        window.open(`/product/${productId}`, '_blank');
    }
}

// Выбор размера товара
function selectSize(productId, size, price) {
    console.log('Выбор размера:', { productId, size, price });
    
    // Убираем выделение со всех кнопок размеров для этого товара
    const sizeButtons = document.querySelectorAll(`[onclick*="selectSize('${productId}'"]`);
    sizeButtons.forEach(btn => btn.classList.remove('selected'));
    
    // Добавляем выделение к выбранному размеру
    event.target.classList.add('selected');
    
    // Сохраняем выбранный размер в localStorage
    localStorage.setItem(`selected_size_${productId}`, size);
    
    // Обновляем кнопку "Добавить в корзину"
    const addToCartBtn = event.target.closest('.product-card').querySelector('.add-to-cart-btn');
    addToCartBtn.onclick = () => addToCart(productId, size, price);
    addToCartBtn.textContent = `Добавить размер ${size}`;
    
    console.log(`Размер ${size} выбран для товара ${productId}`);
}

// Обновленная функция добавления в корзину
function addToCart(productId, size = null, price = null) {
    console.log('addToCart вызвана с:', { productId, size, price });
    
    // Если размер не передан, используем 'default' для товаров без размеров
    if (!size) {
        size = 'default';
        console.log('Размер не указан, используем default');
    }
    
    // Получаем информацию о товаре
    const productCard = event.target.closest('.product-card');
    if (!productCard) {
        console.error('Не найден элемент .product-card');
        return;
    }
    
    const productName = productCard.querySelector('.product-name')?.textContent || 'Товар';
    
    if (!price) {
        const priceElement = productCard.querySelector('.product-price');
        if (priceElement) {
            price = parseFloat(priceElement.textContent.replace('₽', '').replace(/\s/g, ''));
        }
    }
    
    if (!price) {
        console.error('Не удалось получить цену товара');
        return;
    }
    
    const user_id = window.currentUserId || 'demo_user';
    
    console.log('Добавляем в корзину:', { productId, size, price, productName, user_id });
    
    // Добавляем в локальную корзину
    const cartItem = {
        product_id: `${productId}_${size}`,
        name: `${productName} (размер ${size})`,
        price: price,
        quantity: 1,
        size: size
    };
    
    // Добавляем в localStorage
    let localCart = JSON.parse(localStorage.getItem('localCart') || '[]');
    const existingItemIndex = localCart.findIndex(item => item.product_id === cartItem.product_id);
    
    if (existingItemIndex >= 0) {
        localCart[existingItemIndex].quantity += 1;
        console.log('Обновлен существующий товар в корзине');
    } else {
        localCart.push(cartItem);
        console.log('Добавлен новый товар в корзину');
    }
    
    localStorage.setItem('localCart', JSON.stringify(localCart));
    console.log('Локальная корзина обновлена:', localCart);
    
    // Обновляем счетчик корзины
    updateCartCount();
    
    // Отправляем на сервер
    fetch('/api/add-to-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: user_id,
            product_id: productId,
            size: size,
            quantity: 1
        })
    })
    .then(response => {
        console.log('Ответ сервера:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Данные ответа:', data);
        if (data.success) {
            // Показываем уведомление
            showNotification('Товар добавлен в корзину!', 'success');
            
            // Вибрация в Telegram
            if (window.Telegram && window.Telegram.WebApp) {
                window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
            }
        } else {
            showNotification('Ошибка добавления товара: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка добавления в корзину:', error);
        showNotification('Ошибка добавления товара', 'error');
    });
}

// Обновление счетчика корзины
async function updateCartCount() {
    try {
        // Сначала получаем данные с сервера
        try {
            const response = await fetch(`/api/cart/${window.currentUserId || 'demo_user'}`);
            const data = await response.json();
            
            if (data.cart_items && data.cart_items.length > 0) {
                // Обновляем локальную корзину данными с сервера
                window.localCart = data.cart_items;
                
                // Считаем общее количество товаров
                const count = window.localCart.reduce((total, item) => total + item.quantity, 0);
                
                // Обновляем счетчики в интерфейсе
                const cartCountElements = document.querySelectorAll('#cart-count, #floating-cart-count');
                cartCountElements.forEach(element => {
                    element.textContent = count;
                });
                
                // Показываем плавающую кнопку всегда
                const floatingCart = document.querySelector('.floating-cart');
                if (floatingCart) {
                    floatingCart.style.display = 'flex';
                }
                
                // Обновляем главную кнопку Telegram
                if (window.Telegram && window.Telegram.WebApp && count > 0) {
                    const tg = window.Telegram.WebApp;
                    tg.MainButton.text = `Корзина (${count})`;
                    if (!tg.MainButton.isVisible) {
                        tg.MainButton.show();
                    }
                }
                
                console.log('Счетчик корзины обновлен:', count);
            } else {
                // Корзина пуста
                const cartCountElements = document.querySelectorAll('#cart-count, #floating-cart-count');
                cartCountElements.forEach(element => {
                    element.textContent = '0';
                });
                
                // Показываем плавающую кнопку всегда
                const floatingCart = document.querySelector('.floating-cart');
                if (floatingCart) {
                    floatingCart.style.display = 'flex';
                }
                
                // Скрываем главную кнопку Telegram
                if (window.Telegram && window.Telegram.WebApp) {
                    const tg = window.Telegram.WebApp;
                    if (tg.MainButton.isVisible) {
                        tg.MainButton.hide();
                    }
                }
                
                console.log('Корзина пуста');
            }
        } catch (serverError) {
            console.warn('Server sync failed:', serverError);
            // Если сервер недоступен, используем локальную корзину
            let count = 0;
            if (window.localCart) {
                count = window.localCart.reduce((total, item) => total + item.quantity, 0);
            }
            
            const cartCountElements = document.querySelectorAll('#cart-count, #floating-cart-count');
            cartCountElements.forEach(element => {
                element.textContent = count;
            });
        }
        
    } catch (error) {
        console.error('Error updating cart count:', error);
    }
}

// Инициализация локальной корзины
function initLocalCart() {
    if (!window.localCart) {
        window.localCart = [];
    }
}

// Открытие корзины
function openCart() {
    if (window.Telegram && window.Telegram.WebApp) {
        window.location.href = '/cart';
    } else {
        // В браузере показываем модальное окно
        const modal = document.getElementById('cart-modal');
        if (modal) {
            modal.style.display = 'block';
            loadCartContent();
        }
    }
}

// Закрытие корзины
function closeCart() {
    const modal = document.getElementById('cart-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Загрузка содержимого корзины в модальное окно
async function loadCartContent() {
    try {
        const cartContent = document.getElementById('cart-content');
        if (!cartContent) return;
        
        // Используем локальную корзину
        const cartItems = window.localCart || [];
        
        if (cartItems.length === 0) {
            cartContent.innerHTML = `
                <div class="empty-cart">
                    <div class="empty-cart-icon">🛒</div>
                    <h2>Корзина пуста</h2>
                    <p>Добавьте товары из каталога</p>
                </div>
            `;
        } else {
            let html = '<div class="cart-items">';
            let total = 0;
            
            cartItems.forEach(item => {
                const itemTotal = item.price * item.quantity;
                total += itemTotal;
                
                html += `
                    <div class="cart-item" data-product-id="${item.product_id}">
                        <div class="cart-item-image">
                            ${item.image ? `<img src="${item.image}" alt="${item.name}" class="cart-item-img">` : '<div class="cart-item-placeholder">📷</div>'}
                        </div>
                        <div class="cart-item-info">
                            <h3 class="cart-item-name">${item.name}</h3>
                            <div class="cart-item-details">
                                <span class="cart-item-size">Размер: ${item.size || 'Не указан'}</span>
                                <span class="cart-item-price">${item.price.toLocaleString()} ₽</span>
                            </div>
                            <div class="cart-item-quantity">Количество: ${item.quantity} шт</div>
                        </div>
                        <div class="cart-item-controls">
                            <div class="cart-item-total">${itemTotal.toLocaleString()} ₽</div>
                            <button class="remove-btn" onclick="removeFromCart('${item.product_id}')">
                                🗑️
                            </button>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            html += `
                <div class="cart-summary">
                    <div class="summary-row total">
                        <span>Итого:</span>
                        <span>${total.toLocaleString()} ₽</span>
                    </div>
                </div>
                <div class="cart-actions">
                    <button class="clear-cart-btn" onclick="clearCart()">
                        🗑️ Очистить корзину
                    </button>
                    <button class="checkout-btn" onclick="goToCheckout()">
                        💳 Оформить заказ
                    </button>
                </div>
            `;
            
            cartContent.innerHTML = html;
        }
        
        // Синхронизируем с сервером в фоне
        try {
            const response = await fetch(`/api/cart/${currentUserId}`);
            const data = await response.json();
            if (data.cart_items && data.cart_items.length > 0) {
                window.localCart = data.cart_items;
                // Перезагружаем содержимое корзины
                loadCartContent();
            }
        } catch (serverError) {
            console.warn('Server sync failed:', serverError);
        }
        
    } catch (error) {
        console.error('Error loading cart:', error);
    }
}



// Удаление товара из корзины
function removeFromCart(productId) {
    if (!window.localCart) return;
    
    window.localCart = window.localCart.filter(item => item.product_id !== productId);
    updateCartCount();
    loadCartContent();
}

// Очистка корзины
function clearCart() {
    if (confirm('Вы уверены, что хотите очистить корзину?')) {
        window.localCart = [];
        updateCartCount();
        loadCartContent();
    }
}

// Переход к оформлению заказа
function goToCheckout() {
    closeCart();
    window.location.href = '/cart';
}

// Показать уведомление
function showNotification(message, type = 'info') {
    if (window.Telegram && window.Telegram.WebApp) {
        if (type === 'success') {
            window.Telegram.WebApp.showAlert(message);
        } else if (type === 'error') {
            window.Telegram.WebApp.showAlert(message);
        } else {
            window.Telegram.WebApp.showAlert(message);
        }
    } else {
        // Создаем простое уведомление для браузера
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--tg-theme-button-color, #3390ec);
            color: var(--tg-theme-button-text-color, #ffffff);
            padding: 12px 16px;
            border-radius: 8px;
            z-index: 3000;
            font-size: 14px;
            max-width: 300px;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Показать/скрыть индикатор загрузки
function showLoading(show) {
    // Простая реализация индикатора загрузки
    let loader = document.querySelector('.loader');
    
    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.className = 'loader';
            loader.innerHTML = '⏳ Загрузка...';
            loader.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: var(--tg-theme-secondary-bg-color, #f5f5f5);
                padding: 20px;
                border-radius: 12px;
                z-index: 3000;
                font-size: 16px;
            `;
            document.body.appendChild(loader);
        }
    } else {
        if (loader) {
            loader.remove();
        }
    }
}

// Закрытие модального окна при клике вне его
window.addEventListener('click', function(event) {
    const modal = document.getElementById('cart-modal');
    if (event.target === modal) {
        closeCart();
    }
});

// Обработка ошибок сети
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
});

// Предотвращение стандартного поведения при клике на ссылки в Telegram
document.addEventListener('click', function(event) {
    if (window.Telegram && window.Telegram.WebApp) {
        // Позволяем обычное поведение для внутренних ссылок
        const target = event.target.closest('a');
        if (target && target.href && target.href.startsWith(window.location.origin)) {
            // Оставляем стандартное поведение
            return;
        }
    }
});

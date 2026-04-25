const USER_ID = "user123";

document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
    fetchCart();

    document.getElementById('cart-toggle').addEventListener('click', toggleCart);
    document.getElementById('close-cart').addEventListener('click', toggleCart);
    document.getElementById('overlay').addEventListener('click', toggleCart);
});

async function fetchProducts() {
    try {
        const response = await fetch('/api/catalog/products');
        const data = await response.json();
        
        const container = document.getElementById('products-list');
        container.innerHTML = '';
        
        data.products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.innerHTML = `
                <img src="${product.image_url}" alt="${product.name}" class="product-img">
                <div class="product-info">
                    <div class="product-title">${product.name}</div>
                    <div class="product-price">$${product.price.toFixed(2)}</div>
                    <button class="add-btn" onclick="addToCart('${product.id}', '${product.name}', ${product.price})">Add to Cart</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        document.getElementById('products-list').innerHTML = '<div class="loader">Failed to load products. Wait for database to initialize and refresh.</div>';
    }
}

async function fetchCart() {
    try {
        const response = await fetch(`/api/cart/${USER_ID}`);
        const data = await response.json();
        renderCart(data.cart);
    } catch (error) {
        console.error("Cart error", error);
    }
}

async function addToCart(id, name, price) {
    try {
        const response = await fetch(`/api/cart/${USER_ID}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: id, name: name, price: price, quantity: 1 })
        });
        const data = await response.json();
        renderCart(data.cart);
        
        // Dynamic animation 
        const cartIcon = document.querySelector('.cart-icon');
        cartIcon.style.transform = 'scale(1.1)';
        setTimeout(() => cartIcon.style.transform = 'scale(1)', 150);

    } catch (error) {
        console.error("Error adding to cart", error);
    }
}

async function clearCart() {
    await fetch(`/api/cart/${USER_ID}`, { method: 'DELETE' });
    renderCart([]);
    toggleCart();
}

function renderCart(cartItems) {
    const container = document.getElementById('cart-items');
    container.innerHTML = '';
    
    let totalItems = 0;
    
    cartItems.forEach(item => {
        totalItems += item.quantity;
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <div class="item-info">
                <h4>${item.name || 'Product ' + item.product_id}</h4>
                <p>$${item.price ? item.price.toFixed(2) : '0.00'} x ${item.quantity}</p>
            </div>
            <strong>$${((item.price || 0) * item.quantity).toFixed(2)}</strong>
        `;
        container.appendChild(div);
    });

    if (cartItems.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center;">Your cart is empty.</p>';
    }

    document.getElementById('cart-count').innerText = totalItems;
}

function toggleCart() {
    document.getElementById('cart-sidebar').classList.toggle('open');
    document.getElementById('overlay').classList.toggle('show');
}

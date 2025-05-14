document.addEventListener('DOMContentLoaded', function () {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartItemsEl = document.getElementById('cart-items');
    const emptyCartMessage = document.getElementById('empty-cart-message');
    const cartCounter = document.getElementById('cart-counter');
    const deliveryFee = parseFloat(document.getElementById('delivery-fee')?.textContent.replace('$', '') || '4.99');
    let subtotal = 0;

    // Show cart count in checkout
    cartCounter.textContent = cart.length;

    if (cart.length === 0) {
        // Show empty cart message
        emptyCartMessage.classList.remove('hidden');
        cartItemsEl.classList.add('hidden');
        return;
    }

    try {
        cart.forEach(item => {
            subtotal += item.price * item.quantity;
            const clone = document.getElementById('cart-item-template').content.cloneNode(true);

            clone.querySelector('.item-name').textContent =
                `${item.name} ${item.quantity > 1 ? `* ${item.quantity}` : ''}`;
            clone.querySelector('.item-price').textContent =
                `$${(item.price * item.quantity).toFixed(2)}`;

            const removeBtn = clone.querySelector('.remove-btn');
            removeBtn.dataset.id = item.id;

            removeBtn.addEventListener('click', function () {
                const itemId = this.dataset.id;
                const updatedCart = cart.filter(item => item.id != itemId);
                localStorage.setItem('cart', JSON.stringify(updatedCart));

                this.closest('.cart-item').remove();
                cartCounter.textContent = updatedCart.length;

                const newSubtotal = updatedCart.reduce((acc, curr) => acc + curr.price * curr.quantity, 0);
                document.getElementById('subtotal').textContent = `$${newSubtotal.toFixed(2)}`;
                document.getElementById('total').textContent = `$${(newSubtotal + deliveryFee).toFixed(2)}`;
                document.getElementById('final-total').textContent = (newSubtotal + deliveryFee).toFixed(2);

                if (updatedCart.length === 0) {
                    // Show empty cart message and hide items
                    emptyCartMessage.classList.remove('hidden');
                    cartItemsEl.classList.add('hidden');
                }
            });

            cartItemsEl.appendChild(clone);
        });

        // Set initial totals
        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('total').textContent = `$${(subtotal + deliveryFee).toFixed(2)}`;
        document.getElementById('final-total').textContent = (subtotal + deliveryFee).toFixed(2);

    } catch (error) {
        console.error('There was an error processing the cart:', error);
        alert('There was an error loading the cart, please try again!');
    }

    // DELIVERY TIME ESTIMATION
    document.getElementById('calculate-time').addEventListener('click', function (e) {
        e.preventDefault();
        const address = document.getElementById('delivery-address').value.trim();

        if (address.length < 10) {
            alert('Please enter a complete delivery address');
            return;
        }

        const calculateBtn = this;
        calculateBtn.disabled = true;
        calculateBtn.textContent = 'Calculating...';

        setTimeout(() => {
            const isPeakHours = new Date().getHours() >= 17 && new Date().getHours() <= 20;
            const baseTime = Math.floor(Math.random() * 30) + (isPeakHours ? 20 : 15);
            const isBusy = Math.random() < 0.3 || isPeakHours;

            document.getElementById('delivery-result').classList.remove('hidden');
            document.getElementById('time-estimate').textContent =
                `${baseTime}${isBusy ? '+10' : ''} minutes`;

            if (isBusy) {
                document.getElementById('busy-notice').classList.remove('hidden');
            }

            calculateBtn.disabled = false;
            calculateBtn.textContent = 'Calculate Delivery Time';
        }, 1500);
    });

    // FORM SUBMIT
    document.getElementById('checkout-form').addEventListener('submit', function (e) {
        e.preventDefault();

        if (cart.length === 0) {
            alert('Your cart is empty.');
            return;
        }

        const cardNumber = document.getElementById('card-number').value.replace(/\s/g, '');
        const expiry = document.getElementById('card-expiry').value;
        const cvv = document.getElementById('card-cvv').value;

        if (!/^\d{16}$/.test(cardNumber)) {
            alert('Please enter a valid 16-digit card number');
            return;
        }

        if (!/^\d{2}\/\d{2}$/.test(expiry)) {
            alert('Please enter expiry date in MM/YY format');
            return;
        }

        const [month, year] = expiry.split('/').map(n => parseInt(n, 10));
        const now = new Date();
        const expiryDate = new Date(`20${year}`, month);
        if (expiryDate <= now || month < 1 || month > 12) {
            alert('Invalid or expired expiry date');
            return;
        }

        if (!/^\d{3,4}$/.test(cvv)) {
            alert('Please enter a valid CVV');
            return;
        }

        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';

        const deliveryDetails = {
            address: document.getElementById('delivery-address').value,
            instructions: document.getElementById('delivery-instructions').value
        };

        const orderData = {
            cart: cart,
            payment: {
                cardNumber: cardNumber,
                expiry: expiry,
                cvv: cvv
            },
            address: deliveryDetails
        };

        fetch('/place_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                localStorage.removeItem('cart');
                window.location.href = data.redirect;
            } else {
                alert('Error: ' + data.error);
                submitBtn.disabled = false;
                submitBtn.textContent = 'Place Order';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error processing your order');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Place Order';
        });
    });
});

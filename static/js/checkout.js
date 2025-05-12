// load cart from local storage
// wait for DOM to fully load before executing JS
document.addEventListener('DOMContentLoaded', function() {
    // retrieve cart data from localStorage or default to empty array if none exists
    const cart = JSON.parse(localStorage.getItem('cart')) || [];

    // Get reference to the cart items container in the HTML
    const cartItemsEl = document.getElementById('cart-items');
    // get reference to the hidden template for cart items
    const template = document.getElementById('cart-item-template');

    // Show empty message if no items
    if (cart.length === 0) {
    document.getElementById('empty-cart-message').classList.remove('hidden');
    return;
    }

    // Render each cart item
    try {
    let subtotal = 0; // initialize subtotal counter
    cart.forEach(item => { // loop through each item in the cart
        subtotal += item.price * item.quantity; // calculate item total and add to subtotal
        const clone = template.content.cloneNode(true); // clone template to create a new cart item element

        // populate the item name, showing quantity if more than 1
        clone.querySelector('.item-name').textContent =
            `${item.name} ${item.quantity > 1 ? `* ${item.quantity}` : ''}`;

        // format and display the item's total price
        clone.querySelector('.item-price').textContent =
            `$${(item.price * item.quantity).toFixed(2)}`;
        // set the item ID on the remove button for identification
        const removeBtn = clone.querySelector('.remove-btn');
        removeBtn.dataset.id = item.id;

        
    
    // attach event directly to remove button for dynamic removal
    removeBtn.addEventListener('click', function () {
        const itemId = this.dataset.id;
        const updatedCart = cart.filter(item => item.id != itemId);
        localStorage.setItem('cart', JSON.stringify(updatedCart));

        this.closest('.cart-item').remove(); 

        // update totals dynamically
        const newSubtotal = updatedCart.reduce((acc, curr) => acc + curr.price * curr.quantity, 0);
        document.getElementById('subtotal').textContent = `$${newSubtotal.toFixed(2)}`;
        document.getElementById('total').textContent = `$${(newSubtotal + deliveryFee).toFixed(2)}`;
        document.getElementById('final-total').textContent = (newSubtotal + deliveryFee).toFixed(2);

        if (updatedCart.length === 0) {
            document.getElementById('empty-cart-message').classList.remove('hidden');
            document.getElementById('cart-items').innerHTML = '';
        }
    });

    cartItemsEl.appendChild(clone); // add populated item to the cart display

});

    // Calculate totals
    const deliveryFee = parseFloat(document.getElementById('delivery-fee')?.textContent || '3.99');
    // display subtotal (format two decimal places)
    document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
    // calculate and display total
    document.getElementById('total').textContent = `$${(subtotal + deliveryFee).toFixed(2)}`;
    // update order btn with final total
    document.getElementById('final-total').textContent = (subtotal + deliveryFee).toFixed(2);



    } catch (error) {
        console.error('There was an error processing the cart:', error);
        alert('There was an error loading the cart, please try again!');
    }

        // delivery time estimation handler
        document.getElementById('calculate-time').addEventListener('click', function(e) {
        e.preventDefault(); // prevent form submission

        const address = document.getElementById('delivery-address').value.trim();

        // validation
        if (address.length < 10) {
            alert('Please enter a complete delivery address');
            return;
        }

        // loading state
        const calculateBtn = this;
        calculateBtn.disabled = true;
        calculateBtn.textContent = 'Calculating...';

        // mock api call
        setTimeout(() => {
            // time calculations
            const isPeakHours = new Date().getHours() >= 17 && new Date().getHours() <= 20;
            const baseTime = Math.floor(Math.random() * 30) + (isPeakHours ? 20 : 15);
            const isBusy = Math.random() < 0.3 || isPeakHours;

            document.getElementById('delivery-result').classList.remove('hidden');
            document.getElementById('time-estimate').textContent =
                `${baseTime}${isBusy ? '+10' : ''} minutes`;

            if (isBusy) {
                document.getElementById('busy-notice').classList.remove('hidden');
            }

            // Reset button state
            calculateBtn.disabled = false;
            calculateBtn.textContent = 'Calculate Delivery Time';
        }, 1500);
    });

    // FORM SUBMISSION
    document.getElementById('checkout-form').addEventListener('submit', function(e) {
        e.preventDefault();

        // Prevent checkoutif cart is empty
        if (cart.length === 0) {
            alert('Your cart is empty.');
            return;
        }

         // validation
         const cardNumber = document.getElementById('card-number').value.replace(/\s/g, '');
         const expiry = document.getElementById('card-expiry').value;
         const cvv = document.getElementById('card-cvv').value
 
         if (!/^\d{16}$/.test(cardNumber)) {
             alert('Please enter a valid 16-digit card number');
             return;
         }
 
         // Check expiry date
         if (!/^\d{2}\/\d{2}$/.test(expiry)) {
             alert('Please enter expiry date in MM/YY format');
             return;
         }
 
         // check if expiry date is in the future
         const [month, year] = expiry.split('/').map(n => parseInt(n, 10));
         const now = new Date();
         const expiryDate = new Date(`20${year}`, month);
         if (expiryDate <= now) {
             alert('Your card is expired');
             return;
         }
 
         // Check CVV
         if (!/^\d{3,4}$/.test(cvv)) {
             alert('Please enter a valid CVV');
             return;
         }

        // show the processing state
        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textConent = 'Processing...';
        document.getElementById('loading-overlay').classList.remove('hidden');

        // get delivery details
        const deliveryDetails = {
            address: document.getElementById('delivery-address').value,
            instructions: document.getElementById('delivery-instructions').value
        };

        // prepare order data
        const orderData = {
            cart: cart,
            payment: {
                cardNumber: cardNumber,
                expiry: expiry,
                cvv: cvv
            },
            address: deliveryDetails
        };

        // send to server
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
                alert('Error ' + data.error);
                submitBtn.disabled = false;
                submitBtn.textContent = 'Place Order';
                document.getElementById('loading-overlay').classList.add('hidden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error processing your order');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Place Order';
            document.getElementById('loading-overlay').classList.add('hidden;');
        });
    });

});

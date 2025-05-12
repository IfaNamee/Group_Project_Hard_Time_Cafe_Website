document.addEventListener('DOMContentLoaded', function() {
    // Add to cart functionality
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const item = {
                id: parseInt(this.dataset.id, 10),
                name: this.dataset.name,
                price: parseFloat(this.dataset.price),
                quantity: 1
            };
            // get or create cart
            let cart = JSON.parse(localStorage.getItem('cart')) || [];

            // check if item is in cart
            const existingItem = cart.find(cartItem => cartItem.id === item.id);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push(item);
            }
            // save to localStorage
            localStorage.setItem('cart', JSON.stringify(cart));
            // show confirmation 
            alert(`${item.name} added to cart!`);
            
        });
    });

    // add cart counter 
    function updateCartCounter() {
        const cart = JSON.parse(localStorage.getItem('cart')) || [];
        const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
        const counter = document.getElementById('cart-counter');
        if (counter) {
            counter.textContent = totalItems;
            counter.style.display = totalItems > 0 ? 'block' : 'none';
        }
    }

    // update counter on page load
    updateCartCounter();


})
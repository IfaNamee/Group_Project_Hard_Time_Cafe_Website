document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('user-form');
    const loadBtn = document.getElementById('load-saved-cart');
    const savedCartList = document.getElementById('saved-cart-list');

    // Load existing user data
    const existingUser = JSON.parse(localStorage.getItem('userAccount')) || {};
    if (existingUser.username) {
        document.getElementById('username').value = existingUser.username;
        document.getElementById('password').value = existingUser.password;
        document.getElementById('saved-address').value = existingUser.address || '';
        document.getElementById('saved-card').value = existingUser.cardNumber || '';
        document.getElementById('saved-expiry').value = existingUser.expiry || '';
        document.getElementById('saved-cvv').value = existingUser.cvv || '';
    }

    if (existingUser.profilePic) {
        const img = document.createElement('img');
        img.src = existingUser.profilePic;
        img.alt = "Profile Picture";
        img.classList.add("profile-pic-preview");
        form.prepend(img);
    }

    // Handle form submission
    form.addEventListener('submit', e => {
        e.preventDefault();

        const reader = new FileReader();
        const file = document.getElementById('profile-pic').files[0];

        const saveUser = (profilePicData = null) => {
            const userData = {
                username: document.getElementById('username').value.trim(),
                password: document.getElementById('password').value,
                address: document.getElementById('saved-address').value,
                cardNumber: document.getElementById('saved-card').value,
                expiry: document.getElementById('saved-expiry').value,
                cvv: document.getElementById('saved-cvv').value,
                profilePic: profilePicData || existingUser.profilePic || null,
                savedCart: JSON.parse(localStorage.getItem('cart')) || []
            };

            localStorage.setItem('userAccount', JSON.stringify(userData));
            alert('Account info saved!');
        };

        if (file) {
            reader.onload = function (e) {
                saveUser(e.target.result); // base64 string
            };
            reader.readAsDataURL(file);
        } else {
            saveUser();
        }
    });

    // Load saved cart items
    loadBtn.addEventListener('click', () => {
        const account = JSON.parse(localStorage.getItem('userAccount'));
        if (account?.savedCart?.length > 0) {
            savedCartList.innerHTML = '';
            account.savedCart.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.name} x${item.quantity} = $${item.price}`;
                savedCartList.appendChild(li);
            });
        } else {
            alert('No saved cart found!');
        }
    });

    // Update cart counter in navbar
    const updateCartCounter = () => {
        const cart = JSON.parse(localStorage.getItem('cart')) || {};
        let totalCount = 0;
        for (let id in cart) {
            totalCount += cart[id].quantity || 1;
        }
        const counter = document.getElementById('cart-counter');
        if (counter) counter.textContent = totalCount;
    };

    updateCartCounter();
});
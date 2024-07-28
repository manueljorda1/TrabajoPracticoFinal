document.addEventListener('DOMContentLoaded', function () {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const removeFromCartButtons = document.querySelectorAll('.remove-from-cart');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const url = this.getAttribute('href');
            fetch(url)
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });

    removeFromCartButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const url = this.getAttribute('href');
            fetch(url)
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });
});

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerText = message;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function updateCartCount() {
    const cartLink = document.querySelector('nav ul li a[href*="cart"]');
    if (cartLink) {
        fetch('/cart')
            .then(response => response.text())
            .then(data => {
                const cartCount = (data.match(/<div class="producto">/g) || []).length;
                cartLink.innerText = `Carrito (${cartCount})`;
            });
    }
}

const styles = `
.notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #28a745;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    opacity: 0.9;
    transition: opacity 0.3s ease-in-out;
}
`;
const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);



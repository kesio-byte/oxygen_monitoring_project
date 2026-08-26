// app.js

// Mobile menu toggle
const menuBtn = document.getElementById('menu-btn');
const mobileMenu = document.getElementById('mobile-menu');
if (menuBtn) {
    menuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });
}

// Auto-dismiss toasts after 4 seconds
setTimeout(() => {
    document.querySelectorAll('#toast-container .toast').forEach(toast => {
        toast.classList.add('opacity-0'); // fade out
        setTimeout(() => toast.remove(), 500); // remove after fade
    });
}, 4000);

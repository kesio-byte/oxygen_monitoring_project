// app.js

document.addEventListener("DOMContentLoaded", () => {
  // Mobile menu toggle
  const menuBtn = document.getElementById("menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener("click", () => {
      const isHidden = mobileMenu.classList.toggle("hidden");
      menuBtn.setAttribute("aria-expanded", String(!isHidden));
    });
  }

  // Auto-dismiss toast notifications after 4 seconds
  const dismissToasts = () => {
    document
      .querySelectorAll("#toast-container .toast")
      .forEach(toast => {
        toast.classList.add("opacity-0");

        setTimeout(() => {
          toast.remove();
        }, 500);
      });
  };

  setTimeout(dismissToasts, 4000);
});
const menuToggle = document.querySelector(".menu-toggle");
const sidebar = document.querySelector(".sidebar");
const overlay = document.querySelector(".sidebar-overlay");

if (menuToggle && sidebar && overlay) {
    const toggleMenu = () => {
        const isOpen = sidebar.classList.toggle("open");
        overlay.classList.toggle("open", isOpen);
        menuToggle.setAttribute("aria-expanded", String(isOpen));
    };

    menuToggle.addEventListener("click", toggleMenu);
    overlay.addEventListener("click", toggleMenu);
}

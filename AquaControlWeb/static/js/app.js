(() => {
    const menuToggle = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.querySelector(".sidebar-overlay");

    if (!menuToggle || !sidebar || !overlay) {
        return;
    }

    const setMenuOpen = (isOpen) => {
        sidebar.classList.toggle("open", isOpen);
        overlay.classList.toggle("open", isOpen);
        menuToggle.setAttribute("aria-expanded", String(isOpen));
        document.body.classList.toggle("menu-open", isOpen);
    };

    const closeMenu = () => setMenuOpen(false);

    menuToggle.addEventListener("click", () => {
        setMenuOpen(!sidebar.classList.contains("open"));
    });
    overlay.addEventListener("click", closeMenu);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });
    window.addEventListener("resize", () => {
        if (window.innerWidth > 700) {
            closeMenu();
        }
    });
})();

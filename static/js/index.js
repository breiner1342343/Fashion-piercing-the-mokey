document.addEventListener("DOMContentLoaded", () => {
    // 1. LÓGICA DE INTERACTIVIDAD DEL MENÚ MÓVIL
    const menuBtn = document.getElementById("mobileMenuBtn");
    const mobileMenu = document.getElementById("mobileMenu");

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener("click", () => {
            menuBtn.classList.toggle("active");
            mobileMenu.classList.toggle("active");
        });

        const menuLinks = mobileMenu.querySelectorAll("a");
        menuLinks.forEach(link => {
            link.addEventListener("click", () => {
                menuBtn.classList.remove("active");
                mobileMenu.classList.remove("active");
            });
        });
    }
});

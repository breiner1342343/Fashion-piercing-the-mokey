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
document.addEventListener('DOMContentLoaded', () => {
    const userNav = document.getElementById('user-nav-container');
    const userName = localStorage.getItem('user_name'); // O tu método de sesión

    if (userName) {
        userNav.innerHTML = `
            <span class="welcome-text">
                <i class='bx bx-user-circle'></i> Bienvenido, <strong>${userName}</strong>
            </span>
            <a href="/logout" class="btn-logout" title="Cerrar Sesión"><i class='bx bx-log-out'></i></a>
        `;
    }
});

document.addEventListener("DOMContentLoaded", () => {
    
    // ==========================================
    // 1. LÓGICA DE INTERACTIVIDAD DEL MENÚ MÓVIL
    // ==========================================
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

    // ==========================================
    // 2. CONTADOR LENTO AL APARECER EN PANTALLA
    // ==========================================
    const counters = document.querySelectorAll('.count-number');

    // Función encargada de hacer el incremento suave y lento
    const startCounting = (counter) => {
        const target = +counter.getAttribute('data-target');
        let current = 0;
        
        // Regulador de velocidad: entre más alto el número, más lento irá
        const duration = 2000; // 2000 milisegundos = 2 segundos en total para llegar al final
        const frameRate = 1000 / 60; // 60 fotogramas por segundo para máxima fluidez
        const totalFrames = Math.round(duration / frameRate);
        const increment = target / totalFrames;
        let frame = 0;

        const animate = () => {
            frame++;
            current += increment;

            if (frame < totalFrames) {
                // Mostramos el número redondeado
                counter.innerText = Math.floor(current);
                setTimeout(animate, frameRate);
            } else {
                // Al final aseguramos el número exacto
                counter.innerText = target;
            }
        };

        animate();
    };

    // CREACIÓN DEL SENSOR VISUAL (Intersection Observer)
    const observerOptions = {
        root: null, // Usa la pantalla del navegador como base
        threshold: 0.3 // El contador arranca cuando el 30% de la tarjeta ya es visible
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            // Si la tarjeta entró en la pantalla...
            if (entry.isIntersecting) {
                const currentCounter = entry.target;
                startCounting(currentCounter); // Arranca la animación lenta
                observer.unobserve(currentCounter); // Deja de vigilarla para que no se repita al subir y bajar
            }
        });
    }, observerOptions);

    // Le decimos al sensor que vigile cada uno de tus números
    counters.forEach(counter => {
        observer.observe(counter);
    });
});
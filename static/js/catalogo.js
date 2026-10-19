document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Funcionalidad para añadir productos al carrito desde el catálogo
    const botonesAdd = document.querySelectorAll('.btn-add');
    
    botonesAdd.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productoId = this.getAttribute('data-id');
            
            // Redirige al usuario de forma limpia a la ruta de Flask para guardar el producto
            window.location.href = `/agregar/${productoId}`;
        });
    });

    // 2. Funcionalidad para el botón de Proceder al Pago / Pagar en la vista de carrito
    const btnCheckout = document.querySelector('.btn-checkout');
    if (btnCheckout) {
        btnCheckout.addEventListener('click', () => {
            alert("¡Gracias por tu compra en Fashion Piercing The Monkey's!");
            // Opcional: Redirigir a una ruta de finalización de compra en Flask
            // window.location.href = '/checkout';
        });
    }

});
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const suggestionsBox = document.getElementById('suggestionsBox');

    // Extraemos los nombres de los productos directamente de las tarjetas visibles en el catálogo
    // O puedes definir una lista estática de palabras clave si prefieres.
    const obtenerNombresProductos = () => {
        const titulosTarjetas = document.querySelectorAll('.card h3, .card-body h3, h3'); // Ajusta según la clase de tus títulos de productos
        let nombres = new Set();
        titulosTarjetas.forEach(card => {
            if(card.textContent.trim() !== '') {
                nombres.add(card.textContent.trim());
            }
        });
        return Array.from(nombres);
    };

    const listaSugerencias = obtenerNombresProductos();

    if (searchInput && suggestionsBox) {
        searchInput.addEventListener('input', function() {
            const texto = this.value.toLowerCase().trim();
            suggestionsBox.innerHTML = '';

            if (texto === '') {
                suggestionsBox.style.display = 'none';
                return;
            }

            // Filtrar productos que coincidan con lo que escribes
            const coincidencias = listaSugerencias.filter(item => 
                item.toLowerCase().includes(texto)
            );

            if (coincidencias.length > 0) {
                // Título de la sección "SUGERENCIAS" estilo Instagram
                let htmlContent = '<div class="suggestions-title">Sugerencias</div>';
                
                coincidencias.forEach(item => {
                    htmlContent += `<div class="suggestion-item">${item}</div>`;
                });

                suggestionsBox.innerHTML = htmlContent;
                suggestionsBox.style.display = 'block';

                // Hacer clic en una sugerencia para autocompletar y buscar
                document.querySelectorAll('.suggestion-item').forEach(el => {
                    el.addEventListener('click', function() {
                        searchInput.value = this.textContent;
                        suggestionsBox.style.display = 'none';
                        searchInput.form.submit(); // Envía el formulario automáticamente
                    });
                });
            } else {
                suggestionsBox.style.display = 'none';
            }
        });

        // Ocultar sugerencias si haces clic fuera del buscador
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                suggestionsBox.style.display = 'none';
            }
        });
    }
});
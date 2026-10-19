document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    
    if (searchInput) {
        searchInput.addEventListener('keyup', function () {
            const valorBusqueda = this.value.toLowerCase().trim();
            
            // Selecciona todos los elementos que deseas filtrar en el dashboard
            // (filas de tablas, tarjetas de estadísticas o contenedores de elementos)
            const elementosADevolver = document.querySelectorAll('.table-custom tbody tr, .card, .dashboard-card');

            elementosADevolver.forEach(elemento => {
                const textoElemento = elemento.textContent.toLowerCase();
                
                // Si el campo de búsqueda está vacío o el texto coincide, se muestra
                if (valorBusqueda === "" || textoElemento.includes(valorBusqueda)) {
                    elemento.style.display = ''; // Restaura su visualización original
                } else {
                    elemento.style.display = 'none'; // Lo oculta si no coincide
                }
            });
        });
    }
});
        function toggleVista(mostrarFormulario) {
            const tablaSection = document.getElementById('tabla-productos-section');
            const formSection = document.getElementById('form-producto-section');

            if (mostrarFormulario) {
                tablaSection.style.display = 'none';
                formSection.style.display = 'block';
            } else {
                tablaSection.style.display = 'block';
                formSection.style.display = 'none';
            }
        }
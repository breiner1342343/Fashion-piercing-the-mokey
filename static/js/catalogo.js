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
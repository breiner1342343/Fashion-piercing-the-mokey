let carrito = [];

// Agregar ítem al carrito de venta
function agregarAlCarrito(id, nombre, precio) {
    const itemExistente = carrito.find(p => p.id === id);
    if (itemExistente) {
        itemExistente.cantidad++;
    } else {
        carrito.push({ id, nombre, precio, cantidad: 1 });
    }
    actualizarCarritoUI();
}

// Cambiar cantidad de producto
function cambiarCantidad(id, delta) {
    const item = carrito.find(p => p.id === id);
    if (item) {
        item.cantidad += delta;
        if (item.cantidad <= 0) {
            eliminarDelCarrito(id);
        } else {
            actualizarCarritoUI();
        }
    }
}

// Eliminar producto del carrito
function eliminarDelCarrito(id) {
    carrito = carrito.filter(p => p.id !== id);
    actualizarCarritoUI();
}

// Renderizar UI del Carrito y Totales
function actualizarCarritoUI() {
    const tbody = document.getElementById('cartItems');
    tbody.innerHTML = '';

    if (carrito.length === 0) {
        tbody.innerHTML = `
            <tr id="emptyCartRow">
                <td colspan="4" class="empty-msg">No has agregado productos a la venta.</td>
            </tr>`;
        document.getElementById('subtotalText').innerText = '$0';
        document.getElementById('totalText').innerText = '$0';
        return;
    }

    let total = 0;
    carrito.forEach(item => {
        const subtotal = item.precio * item.cantidad;
        total += subtotal;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.nombre}</td>
            <td>
                <div class="qty-controls">
                    <button type="button" class="btn-qty" onclick="cambiarCantidad(${item.id}, -1)">-</button>
                    <span>${item.cantidad}</span>
                    <button type="button" class="btn-qty" onclick="cambiarCantidad(${item.id}, 1)">+</button>
                </div>
            </td>
            <td>$${subtotal.toLocaleString('es-CO')}</td>
            <td>
                <button type="button" class="btn-del" onclick="eliminarDelCarrito(${item.id})">
                    <i class='bx bx-trash'></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('subtotalText').innerText = `$${total.toLocaleString('es-CO')}`;
    document.getElementById('totalText').innerText = `$${total.toLocaleString('es-CO')}`;
}

// Filtrar catálogo por categoría
function filtrarProductos(categoria) {
    const botones = document.querySelectorAll('.filter-btn');
    botones.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    const productos = document.querySelectorAll('.product-item');
    productos.forEach(prod => {
        if (categoria === 'todos' || prod.getAttribute('data-cat') === categoria) {
            prod.style.display = 'flex';
        } else {
            prod.style.display = 'none';
        }
    });
}

// Validar envío del formulario
document.getElementById('formVenta').addEventListener('submit', function (e) {
    if (carrito.length === 0) {
        e.preventDefault();
        alert('Por favor agrega al menos un producto o servicio antes de registrar la venta.');
    }
});
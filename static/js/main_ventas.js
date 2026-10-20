document.addEventListener("DOMContentLoaded", function () {
    // Configuración global de fuentes y colores de Chart.js
    Chart.defaults.color = '#8e9bb0';
    Chart.defaults.font.family = 'Poppins';

    /* =========================================================
       1. GRÁFICO DE BARRAS COMPARATIVO (Ventas Anuales)
       ========================================================= */
    const ctxBar = document.getElementById('barChartResult').getContext('2d');
    
    let barChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            datasets: [
                {
                    label: '2025 (Joyas Vendidas)',
                    data: [18, 38, 20, 32, 28, 30, 20, 22, 28, 35, 40, 50],
                    backgroundColor: '#ffb700', // Dorado
                    borderRadius: 4,
                    barPercentage: 0.5,
                },
                {
                    label: '2026 (Proyección/Actual)',
                    data: [25, 42, 24, 38, 18, 48, 25, 28, 32, 45, 52, 65],
                    backgroundColor: '#1e293b', // Azul oscuro contraste
                    borderRadius: 4,
                    barPercentage: 0.5,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: {
                        boxWidth: 12,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: '#060b13',
                    titleColor: '#ffb700',
                    bodyColor: '#f8fafc',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    beginAtZero: true
                }
            }
        }
    });

    /* =========================================================
       2. GRÁFICO DOUGHNUT (Categorías de Piercing)
       ========================================================= */
    const ctxDoughnut = document.getElementById('doughnutChart').getContext('2d');
    
    new Chart(ctxDoughnut, {
        type: 'doughnut',
        data: {
            labels: ['Titanio ASTM F-136', 'Acero Quirúrgico 316L', 'Oro 14K / Bioplast'],
            datasets: [{
                data: [68, 22, 10],
                backgroundColor: [
                    '#ffb700', // Dorado
                    '#22d3ee', // Cyan
                    '#38bdf8'  // Azul claro
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '78%',
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#060b13',
                    bodyColor: '#f8fafc'
                }
            }
        }
    });

    /* =========================================================
       3. GRÁFICO DE ÁREA SUAVE / ONDAS (Flujo Semanal)
       ========================================================= */
    const ctxWave = document.getElementById('waveChart').getContext('2d');

    // Gradiente de color para Ventas en Tienda
    const gradGold = ctxWave.createLinearGradient(0, 0, 0, 300);
    gradGold.addColorStop(0, 'rgba(255, 183, 0, 0.4)');
    gradGold.addColorStop(1, 'rgba(255, 183, 0, 0.0)');

    // Gradiente de color para Citas Confirmadas
    const gradCyan = ctxWave.createLinearGradient(0, 0, 0, 300);
    gradCyan.addColorStop(0, 'rgba(34, 211, 238, 0.3)');
    gradCyan.addColorStop(1, 'rgba(34, 211, 238, 0.0)');

    new Chart(ctxWave, {
        type: 'line',
        data: {
            labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
            datasets: [
                {
                    label: 'Ventas en Tienda ($)',
                    data: [210, 340, 290, 480, 620, 890, 750],
                    borderColor: '#ffb700',
                    backgroundColor: gradGold,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                },
                {
                    label: 'Citas Confirmadas',
                    data: [150, 220, 180, 310, 410, 580, 490],
                    borderColor: '#22d3ee',
                    backgroundColor: gradCyan,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#060b13',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: { grid: { display: false } },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    beginAtZero: true
                }
            }
        }
    });

    /* =========================================================
       4. BÚSQUEDA INTERACTIVA EN EL DASHBOARD
       ========================================================= */
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            const query = e.target.value.toLowerCase();
            console.log("Filtrando dashboard para:", query);
            // Puedes agregar aquí lógica para filtrar elementos dinámicamente si es necesario
        });
    }
});

/* Funciones externas para botones de filtro */
function updateChartFilter(tipo) {
    const buttons = document.querySelectorAll('.btn-chart-action');
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    console.log("Filtro actualizado a:", tipo);
}
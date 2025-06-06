(function () {

console.log("Hola Orden Inventario");

// function getCSRFToken() {
//     const token = document.querySelector('meta[name="csrf-token"]');
//     return token ? token.content : '';
// }

function formatearFecha(fechaISO) {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}


let dataTable;
let dataTableIsInitialized = false;



const dataTableOptions = {
    columnDefs: [
        { className: "text-center", targets: [0, 1, 2, 3] },
        { orderable: false, targets: [2, 3] },
        { searchable: false, targets: [3] }
    ],
    pageLength: 10,
    destroy: true,
    dom: 'Blfrtip',
    buttons: [
        'excel', 'pdf', 'colvis'
    ],

    language: {
        processing:     "Procesando...",
        lengthMenu:     "Mostrar _MENU_ registros por página",
        zeroRecords:    "No se encontraron resultados",
        emptyTable:     "Ningún dato disponible en esta tabla",
        info:           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
        infoEmpty:      "Mostrando registros del 0 al 0 de un total de 0 registros",
        infoFiltered:   "(filtrado de un total de _MAX_ registros)",
        search:         "Buscar:",
        loadingRecords: "Cargando...",
        paginate: {
            first:    "Primero",
            last:     "Último",
            next:     "Siguiente",
            previous: "Anterior"
        },
        aria: {
            sortAscending:  ": Activar para ordenar de forma ascendente",
            sortDescending: ": Activar para ordenar de forma descendente"
        },
        buttons: {
            // copy: "Copiar",
            colvis: "Visibilidad columnas"
        }
    },

    // ✅ Agrega las opciones de cantidad que puede seleccionar el usuario
    lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]]
};

const initDataTable = async () => {
    if (dataTableIsInitialized) {
        dataTable.destroy();
    }

    await Inventario();

    // Verificamos si la tabla existe antes de inicializar DataTable
    const table = document.getElementById('datatableInventario');
    if (table) {
        dataTable = $('#datatableInventario').DataTable(dataTableOptions);
        dataTableIsInitialized = true;
    }
}


const style = document.createElement('style');
style.textContent = `
    .bg-warning-custom {
        background-color: #ff9800 !important;
        color: white !important;
        padding: 4px 8px;
        border-radius: 5px;
    }
`;
document.head.appendChild(style);

const Inventario = async () => {
    console.log("Inventario...");
    
    try {
        const response = await fetch('/inventario_bodega_json/');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        console.log("Datos combinados:", data);

        const tableBody = document.getElementById('tableBody_inventario');
        if (tableBody) {
            let content = ``;
            data.inventarios.forEach((item, index) => {

                   if (item.stock < 10) {
        colorClass = 'bg-danger text-white fw-bold rounded px-2 py-1'; // rojo
    } else if (item.stock < 20) {
        colorClass = 'bg-warning-custom'; // naranja
    } else {
        colorClass = 'bg-success text-white fw-bold rounded px-2 py-1'; // verde
    }

        
            content += `
                <tr class="text-center">
                    <td>${item.bodega}</td>
                    <td style="text-transform: uppercase;">${item.producto}</td>
                    <td style="text-transform: uppercase;">${item.entradas}</td>
                    <td class="total">${item.salidas}</td>
                    <td><span class="${colorClass}">${item.stock}</span></td>
                    <td >${formatearFecha(item.ultima_entrada)}</td>
                    <td >${formatearFecha(item.ultima_salida)}</td>         
                </tr>
            `;
            });

            tableBody.innerHTML = content;
        }
    } catch (ex) {
        alert("Error: " + ex.message);
        console.error("Error al cargar órdenes y compras:", ex);
    }

    $(".total").number(true, 2);
};


window.addEventListener("load", async () => {
    await initDataTable();
    console.log("Página cargada");
});

})();


    
console.log("Hola orden Compras");

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
    dom: 'Bfrtip',
    buttons: [
        'copy', 'csv', 'excel', 'pdf', 'print', 'colvis'
    ],
    
    // ✅ Traducción al español
    language: {
        processing:     "Procesando...",
        lengthMenu:     "Mostrar _MENU_ registros",
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
            copy: "Copiar",
            colvis: "Visibilidad"
        }
    }
};

const initDataTable = async () => {
    if (dataTableIsInitialized) {
        dataTable.destroy();
    }

    await OrdenCompras();

    // Verificamos si la tabla existe antes de inicializar DataTable
    const table = document.getElementById('datatableOrdenCompra');
    if (table) {
        dataTable = $('#datatableOrdenCompra').DataTable(dataTableOptions);
        dataTableIsInitialized = true;
    }
}

const OrdenCompras = async () => {
    console.log("hola");
    
    try {
    const response = await fetch('/list_orden_compra/');
    
    // Verificamos si la respuesta es correcta
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Respuesta completa:", data);

    if (!Array.isArray(data.orden_compra)) {
        throw new Error("La propiedad 'orden_compra' no es un arreglo o no existe.");
    }

    const tableBody = document.getElementById('tableBody_ordenCompra');
    if (tableBody) {
        let content = ``;
        data.orden_compra.forEach((OrdenCompra, index) => {
            const activo = OrdenCompra.activo === "True" || OrdenCompra.activo === true;

            content += `
                <tr class="text-center">
                    <td style="text-align: center !important;">${OrdenCompra.id}</td>
                    <td>${OrdenCompra.proveedor}</td>
                    <td>${OrdenCompra.fecha}</td>
                    <td>
                        ${activo
                            ? "<i class='fa-solid fa-check' style='color: green;'></i>"
                            : "<i class='fa-solid fa-xmark' style='color: red;'></i>"
                        }
                    </td>
                    <td>
                        <a href="">
                            <button class="btn btn-sm btn-warning">
                                <i class='fa-solid fa-pencil'></i>
                            </button>
                        </a>
                    </td>
                </tr>
            `;
        });
        tableBody.innerHTML = content;
    }
} catch (ex) {
    alert("Error: " + ex.message);
    console.error("Error al obtener ordenes de compra:", ex);
}
}

window.addEventListener("load", async () => {
    await initDataTable();
    console.log("Página cargada");
});
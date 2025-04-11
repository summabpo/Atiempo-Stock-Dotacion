console.log("Hola");

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

    await bodegas();

    // Verificamos si la tabla existe antes de inicializar DataTable
    const table = document.getElementById('datatableBodega');
    if (table) {
        dataTable = $('#datatableBodega').DataTable(dataTableOptions);
        dataTableIsInitialized = true;
    }
}

const bodegas = async () => {
    console.log("hola");
    
    try {
        const response = await fetch('http://127.0.0.1:8000/list_bodegas/');
        const data = await response.json();
        console.log(data.bodegas);      // si el JSON 
        // Verificamos que el tbody exista antes de modificarlo
        const tableBody = document.getElementById('tableBody_bodega');
        if (tableBody) {
            console.log("Hola P");
            
            let content = ``;
            data.bodegas.forEach((bodega, index) => {

                const activo = bodega.activo === "True" || bodega.activo === true;
                content += `
                    <tr class="text-center">
                        <td style=" text-align: center !important;">${bodega.id_bodega}</td>
                        <td>${bodega.nombre}</td>
                        <td>${bodega.ciudad}</td>
                        <td>${bodega.direccion}</td>
                        <td>
            ${activo
                ? "<i class='fa-solid fa-check' style='color: green;'></i>"
                : "<i class='fa-solid fa-xmark' style='color: red;'></i>"
            }
        </td>
                       <td><a href="${bodega.url_editar}"><button class="btn btn-sm btn-warning">
                            <i class='fa-solid fa-pencil'></i>
                        </button></a></td>
                        
                    </tr>
                `;
            });
            tableBody.innerHTML = content;
        }
    } catch (ex) {
        alert(ex);
        console.error("Error al obtener bodegas:", ex);
    }
}

window.addEventListener("load", async () => {
    await initDataTable();
    console.log("Página cargada");
});
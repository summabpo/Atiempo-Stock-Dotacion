(function () {
console.log("empleados");

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
            colvis: "Visibilidad"
        }
    }
};

const initDataTable = async () => {
    if (dataTableIsInitialized) {
        dataTable.destroy();
    }

    await empleadoDotacion();

    // Verificamos si la tabla existe antes de inicializar DataTable
    const table = document.getElementById('datatableEmpleadosAll');
    if (table) {
        dataTable = $('#datatableEmpleadosAll').DataTable(dataTableOptions);
        dataTableIsInitialized = true;
    }
}

const empleadoDotacion = async () => {
    console.log("hola");
    
    try {
        const response = await fetch('/list_empleados/');
        const data = await response.json();
       
        // Verificamos que el tbody exista antes de modificarlo
        const tableBody = document.getElementById('tableBody_empleado');
        if (tableBody) {
            console.log("Hola P");
            
            let content = ``;
            data.empleadoDotacion.forEach((item, index) => {

              
                content += `
                    <tr class="text-center">
                        <td style=" text-align: center !important;">${item.cedula}</td>
                        <td>${item.nombre}</td>
                        <td>${item.ciudad}</td>
                        <td>${item.cargo}</td>
                        <td>${item.cliente}</td>
                        <td>${item.centro_costo}</td>
                        <td>${item.sexo}</td>
                        <td>${item.talla_camisa}</td>
                                    
                        
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

})();
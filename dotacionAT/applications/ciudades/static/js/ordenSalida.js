(function () {

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

console.log("Hola orden salida");

function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.content : '';
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

    await OrdenSalida();

    // Verificamos si la tabla existe antes de inicializar DataTable
    const table = document.getElementById('datatableOrdenSalida');
    if (table) {
        dataTable = $('#datatableOrdenSalida').DataTable(dataTableOptions);
        dataTableIsInitialized = true;
    }
}

const OrdenSalida = async () => {
    console.log("Cargando salidas...");
    
    try {
        const response = await fetch('/list_orden_salida/');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        console.log("Datos combinados:", data);

        const tableBody = document.getElementById('tableBody_ordenSalida');
        if (tableBody) {
            let content = ``;
            data.ordenes_salida.forEach((item, index) => {
                const activo = item.activo === true;
           
            // if(item.tipo_documento == 'OC'){

            //     idTipoDoc =   item.id+' - '+item.tipo_documento;
            // }else if(item.tipo_documento == 'OR'){

            //    idTipoDoc = item.numero_factura+' - '+item.tipo_documento;
            // } 
                
           

            // if(item.tipo_documento == 'OC' && item.estado == 'comprada'){
                
            //     estadoId = item.estado+' # '+item.numero_factura;
                                                
            // }else{
                
            //     estadoId = item.estado;

            // }

            // if(item.tipo_documento == 'OR'){
            //     idTipoDoc = item.numero_factura+' - '+item.tipo_documento;

            // }
            
            let botonCancelar = '';
             let estado = '';
            if (item.tipo_documento == 'OC' && item.estado == 'generada') {
                botonCancelar = `
                    <button title="Cancelar Orden compra" class="btn btn-sm btn-danger" onclick="confirmarCambioEstado('${item.url_cancelar}')">
                        <i class='fa-solid fa-times'></i>
                    </button>
                `;
            }

             if (item.cliente == 'Atiempo SAS' ) {
                estado = `Traslado a Bodega - ${item.bodegaSalida}`;
            }else if (item.cliente != 'Atiempo SAS' ){
                estado =`Salida Cliente`;
            }
        
            content += `
                <tr class="text-center">
                    <td>${item.id}</td>
                    <td style="text-transform: uppercase;">${item.cliente}</td>
                    <td style="text-transform: uppercase;">${estado}</td>
                    <td>${formatearFecha(item.fecha)}</td>
                    <td>
                        <a href="${item.url_editar}">
                            <button title="Ver Detalle Salida" class="btn btn-sm btn-warning">
                                <i class='fa-solid fa-pencil'></i>
                            </button>
                        </a>
                      
                        ${botonCancelar}
                    </td>
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
(function () {
console.log("Hola orden Compras");

function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.content : '';
}


function formatearFecha(fechaISO) {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
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
        'excel', 'pdf','colvis'
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

    await OrdenCompras();

    // Verificamos si la tabla existe antes de inicializar DataTable
    const table = document.getElementById('datatableOrdenCompra');
    if (table) {
        dataTable = $('#datatableOrdenCompra').DataTable(dataTableOptions);
        dataTableIsInitialized = true;
    }
}

const OrdenCompras = async () => {
    console.log("Cargando órdenes y compras...");
    
    try {
        const response = await fetch('/list_orden_y_compra/');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        console.log("Datos combinados:", data);

        const tableBody = document.getElementById('tableBody_ordenCompra');
        if (tableBody) {
            let content = ``;
            data.ordenes_compras.forEach((item, index) => {
                let estadoActual = '';
                const activo = item.activo === true;


            // if(item.tipo_documento == 'OC'){

            //     idTipoDoc =   item.id+' - '+item.tipo_documento;
            // }else if(item.tipo_documento == 'CP'){

            //    idTipoDoc = item.numero_factura+' - '+item.tipo_documento;

            // }else if(item.tipo_documento == 'TRS'){

            //    idTipoDoc = item.id+' - '+item.tipo_documento;

            // }else if(item.tipo_documento == 'TRR'){

            //    idTipoDoc = item.id+' - '+item.tipo_documento;
            // }    

            // console.log(idTipoDoc);
            
                
            if(item.tipo_documento == 'OC' && item.estado == 'comprada'){
                
                estadoId = item.estado+' # '+item.numero_factura;
                                                
            }
            else if(item.tipo_documento == 'TRS'){
                
                 estadoId = `Orden # ${item.salidas_ids} Traslado Bodega`;

            }
            else{
                
                estadoId = item.estado;

            }

            // if(item.tipo_documento == 'OR'){
            //     idTipoDoc = item.numero_factura+' - '+item.tipo_documento;
            // }
        
            let botonCancelar = '';
            if (item.tipo_documento == 'OC' && item.estado == 'generada') {
                botonCancelar = `
                    <button title="Cancelar Orden compra" class="btn btn-sm btn-danger" onclick="confirmarCambioEstado('${item.url_cancelar}')">
                        <i class='fa-solid fa-times'></i>
                    </button>
                `;
            }
            

            if(item.estado == 'generada'){
                
                estadoActual = 'Pendiente Confirmar';

            }else if(item.estado == 'recibida' ){

                 estadoActual = item.estado+' '+item.orden_compra;

            }else if(item.tipo_documento == 'TRR' ){

                 estadoActual = item.orden_compra;

                 estadoId = 'Ingreso Traslado';

            }
            else{

                 estadoActual = '';

            }

          
            let claseEstado = '';
            if (item.estado === 'generada') {
            claseEstado = 'estado-pendiente';
            } else if (item.estado === 'recibida') {
            claseEstado = 'estado-recibida';
            } else if (item.estado === 'Cancelada') {
            claseEstado = 'estado-cancelada';
            }
        
            // if(item.proveedor == ){
            // }

            content += `
                <tr class="text-center ${claseEstado}">
                    <td>${item.id+' - '+item.tipo_documento}</td>
                    <td style="text-transform: uppercase;">${item.proveedor}</td>
                    <td style="text-transform: uppercase;">${estadoId}</td>
                    <td class="total">${item.total}</td> 
                    <td style="text-transform: uppercase;">${estadoActual}</td> 
                    <td>${formatearFecha(item.fecha)}</td>
                    <td style="text-transform: uppercase;">${item.usuario}</td>
                    <td>
                        <a href="${item.url_editar}">
                            <button title="Ver Detalle O C" class="btn btn-sm btn-warning">
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



    // <td>
        //     ${item.activo
        //         ? "<i class='fa-solid fa-check' style='color: green;'></i>"
        //         : "<i class='fa-solid fa-xmark' style='color: red;'></i>"
        //     }
        // </td>

        function confirmarCambioEstado(ordenId) {
            Swal.fire({
                title: '¿Estás seguro?',
                text: "¿Deseas cambiar el estado de esta orden?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, cambiarlo'
            }).then((result) => {
                if (result.isConfirmed) {

                   console.log('Hola');
                   

                    // Puedes usar fetch o enviar un formulario
                    fetch(`${ordenId}`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCSRFToken(),
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ estado: 'CANCELADO' })
                    })
                    
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('Actualizado!', 'El estado fue cambiado.', 'success').then(() => {
                                location.reload();  // refrescar la página o actualizar solo la fila
                            });
                        } else {
                            Swal.fire('Error', data.message || 'No se pudo cambiar el estado.', 'error');
                        }
                    })
                    .catch(err => {
                        console.error(err);
                        Swal.fire('Error', 'Ocurrió un problema al enviar la solicitud.', 'error');
                    });
                }
            });
        }

})();        
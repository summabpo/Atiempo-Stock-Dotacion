(function () {
    
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
    

    await usuarios();

    // Verificamos si la tabla existe antes de inicializar DataTable
    const table = document.getElementById('datatableUsuario');
    if (table) {
        dataTable = $('#datatableUsuario').DataTable(dataTableOptions);
        dataTableIsInitialized = true;
    }
}



 

const usuarios = async () => {
    console.log("hola");
    
    try {
        const response = await fetch('/list_usuarios/');
        const data = await response.json();
        console.log(data.usuarios);      // si el JSON 
        // Verificamos que el tbody exista antes de modificarlo
        const tableBody = document.getElementById('tableBody_usuario');
        if (tableBody) {
            console.log("Hola P");
            
            let content = ``;
            data.usuario.forEach((usuario, index) => {
    
    const rolDisplay = usuario.rol_display || usuario.rol || 'N/A';
    
    // ✅ CORREGIDO: Manejar tanto boolean como string
    const estadoEsActivo = usuario.estado === true || usuario.estado === 'activo';
    const estadoDisplay = estadoEsActivo ? 'Activo' : 'Inactivo';
    
    const fechaCreacion = usuario.fecha_creacion || 'N/A';
    
    content += `
        <tr class="text-center">
            <td>${usuario.id || (index + 1)}</td>
            <td>${usuario.nombre || usuario.username || 'N/A'}</td>
            <td>${usuario.email || 'N/A'}</td>
            <td>${rolDisplay}</td>
            <td>
                ${estadoEsActivo
                    ? `<span class="badge badge-success"><i class='fa-solid fa-check'></i> ${estadoDisplay}</span>`
                    : `<span class="badge badge-danger"><i class='fa-solid fa-xmark'></i> ${estadoDisplay}</span>`
                }
            </td>
            <td>${fechaCreacion}</td>
            <td>
                <a href="/editar/${usuario.id}/" class="btn btn-sm btn-warning" title="Editar">
                    <i class='fa-solid fa-pencil'></i>
                </a>
                
            </td>
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
   
    // Inicializar cuando la página se cargue completamente
    window.addEventListener("load", async () => {
        console.log("Página cargada - Iniciando DataTable");
        await initDataTable();
    });
    // Opcional: Recargar datos si el usuario hace algo (ej: después de editar)
    // Puedes llamar a cargarUsuarios() desde otros eventos
})();



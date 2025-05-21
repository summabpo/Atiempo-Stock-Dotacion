(function () {
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

        await ciudades();

        const table = document.getElementById('datatablePlantilla');
        if (table) {
            dataTable = $('#datatablePlantilla').DataTable(dataTableOptions);
            dataTableIsInitialized = true;
        }
    }

    const ciudades = async () => {
        try {
            const response = await fetch('/list_ciudades/');
            const data = await response.json();
            console.log(data.ciudades);

            // Verificamos que el tbody exista antes de modificarlo
            const tableBody = document.getElementById('tableBody_ciudad');
            if (tableBody) {
                let content = ``;
                data.ciudades.forEach((ciudad, index) => {

                    const activo = ciudad.activo === "True" || ciudad.activo === true;
                    content += `
                        <tr class="text-center">
                            <td style=" text-align: center !important;">${ciudad.id_ciudad}</td>
                            <td>${ciudad.nombre}</td>
                            <td>
                                ${activo
                                    ? "<i class='fa-solid fa-check' style='color: green;'></i>"
                                    : "<i class='fa-solid fa-xmark' style='color: red;'></i>"
                                }
                            </td>
                            <td><a href="${ciudad.url_editar}"><button class="btn btn-sm btn-warning">
                                    <i class='fa-solid fa-pencil'></i>
                                </button></a></td>
                        </tr>
                    `;
                });
                tableBody.innerHTML = content;
            }
        } catch (ex) {
            console.error("Error al obtener ciudades:", ex);
            alert("Ocurrió un error al cargar las ciudades");
        }
    }

    window.addEventListener("load", async () => {
        await initDataTable();
        console.log("Página cargada");
    });
})();
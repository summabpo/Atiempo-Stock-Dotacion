(function () {
    console.log("Hola Bodega");

    let dataTable;
    let dataTableIsInitialized = false;

    const dataTableOptionsBodegas = {
        columnDefs: [
            { className: "text-center", targets: [0, 1, 2, 3] },
            { orderable: false, targets: [2, 3] },
            { searchable: false, targets: [3] }
        ],
        pageLength: 10,
        destroy: true,
        dom: 'Blfrtip',
        buttons: ['excel', 'pdf', 'colvis'],
        language: {
            processing: "Procesando...",
            lengthMenu: "Mostrar _MENU_ registros",
            zeroRecords: "No se encontraron resultados",
            emptyTable: "Ningún dato disponible en esta tabla",
            info: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            infoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
            infoFiltered: "(filtrado de un total de _MAX_ registros)",
            search: "Buscar:",
            loadingRecords: "Cargando...",
            paginate: {
                first: "Primero",
                last: "Último",
                next: "Siguiente",
                previous: "Anterior"
            },
            aria: {
                sortAscending: ": Activar para ordenar de forma ascendente",
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

        await cargarBodegas();

        const table = document.getElementById('datatableBodega');
        if (table) {
            dataTable = $('#datatableBodega').DataTable(dataTableOptionsBodegas);
            dataTableIsInitialized = true;
        }
    };

    const cargarBodegas = async () => {
        try {
            const response = await fetch('/list_bodegas/');
            const data = await response.json();

            const tableBody = document.getElementById('tableBody_bodega');
            if (tableBody) {
                let content = ``;
                data.bodegas.forEach((bodega) => {
                    const activo = bodega.activo === "True" || bodega.activo === true;
                    content += `
                        <tr class="text-center">
                            <td>${bodega.id_bodega}</td>
                            <td>${bodega.nombre}</td>
                            <td>${bodega.ciudad}</td>
                            <td>${bodega.direccion}</td>
                            <td>
                                ${activo
                                    ? "<i class='fa-solid fa-check' style='color: green;'></i>"
                                    : "<i class='fa-solid fa-xmark' style='color: red;'></i>"
                                }
                            </td>
                            <td>
                                <a href="${bodega.url_editar}">
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
            console.error("Error al obtener bodegas:", ex);
            alert("Ocurrió un error al cargar las bodegas");
        }
    };

    window.addEventListener("load", async () => {
        await initDataTable();
        console.log("Página cargada");
    });
})();
// $(document).ready(function () {
//   console.log("lista grupos");


//   let formsetContainer;  // declarar arriba del todo

//     document.addEventListener("DOMContentLoaded", () => {
//         formsetContainer = document.getElementById("formset-container");
//         attachRemoveButtons(); // ahora sí existe
//     });


//   const table = $('#tabla-grupos').DataTable({
//     columnDefs: [
//       { className: "text-center", targets: [0, 1, 2, 3] },
//       { orderable: false, targets: [2, 3] },
//       { searchable: false, targets: [3] }
//     ],
//     language: {
//       processing:     "Procesando...",
//       lengthMenu:     "Mostrar _MENU_ registros",
//       zeroRecords:    "No se encontraron resultados",
//       emptyTable:     "Ningún dato disponible en esta tabla",
//       info:           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
//       infoEmpty:      "Mostrando registros del 0 al 0 de un total de 0 registros",
//       infoFiltered:   "(filtrado de un total de _MAX_ registros)",
//       search:         "Buscar:",
//       loadingRecords: "Cargando...",
//       paginate: {
//         first:    "Primero",
//         last:     "Último",
//         next:     "Siguiente",
//         previous: "Anterior"
//       },
//       aria: {
//         sortAscending:  ": Activar para ordenar de forma ascendente",
//         sortDescending: ": Activar para ordenar de forma descendente"
//       },
//       buttons: {
//         colvis: "Visibilidad"
//       }
//     },

//     // ✅ Usar this.api() para acceder al DataTable
//     initComplete: function () {
//       const api = this.api();
//       api.rows().every(function () {
//         const tr = $(this.node());
//         const detalle = tr.data('detalle');
//         if (detalle) {
//           this.child(detalle).show();
//           tr.addClass('shown');
//         }
//       });
//     }
//   });

//   // ✅ Control para expandir/cerrar al hacer clic
//   $('#tabla-grupos tbody').on('click', 'td.dt-control', function () {
//     const tr = $(this).closest('tr');
//     const row = table.row(tr);

//     if (row.child.isShown()) {
//       row.child.hide();
//       tr.removeClass('shown');
//     } else {
//       const detalle = tr.data('detalle');
//       row.child(detalle).show();
//       tr.addClass('shown');
//     }
//   });
// });

// function aplicarSelect2() {
//     console.log("Aplicando Select2 solo a elementos específicos");
    
//     // Seleccionar SOLO los selects que necesitan Select2
//     // Evita los que están en modales, alerts, etc.
//     $('select:not(.swal2-select, .modal select, [data-no-select2])').select2({
//         width: '100%',
//         theme: 'classic',
//         placeholder: "Seleccione una opción",
//         allowClear: true
//     });
// }

// aplicarSelect2();
// document.addEventListener('DOMContentLoaded', () => {
//     console.log("Hola");

//     const formsetContainer = document.getElementById('formset-container');
//     const prefix = formsetContainer.dataset.prefix;
//     const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
//     const addFormButton = document.getElementById('add-form');

//     // 🟢 Función para actualizar opciones disponibles
//     function actualizarOpcionesDisponibles() {
//         const selects = formsetContainer.querySelectorAll(`select[name^="${prefix}"]`);
//         const seleccionadas = new Set();
//         selects.forEach(sel => {
//             if(sel.value) seleccionadas.add(sel.value);
//         });

//         selects.forEach(sel => {
//             [...sel.options].forEach(opt => {
//                 if(opt.value === "" || opt.value === sel.value) {
//                     opt.disabled = false;
//                 } else {
//                     opt.disabled = seleccionadas.has(opt.value);
//                 }
//             });
//             $(sel).trigger('change.select2');
//         });
//     }

//     // ➕ Agregar nueva fila
//     addFormButton.addEventListener('click', () => {
//         const currentFormCount = parseInt(totalForms.value);
//         const lastForm = formsetContainer.querySelector('.formset-item:last-of-type');

//         // $(lastForm).find('select').select2('destroy');

//         $(lastForm).find('select').each(function() {
//             if ($.fn.select2 && $(this).data('select2')) {
//                 $(this).select2('destroy');
//             }
//         });

//         const newForm = lastForm.cloneNode(true);
//         newForm.querySelectorAll('input, select, textarea').forEach(field => {
//             if(field.tagName === 'SELECT'){
//                 field.selectedIndex = 0;
//             } else {
//                 field.value = '';
//             }
//         });

//         // Renumerar indices
//         newForm.innerHTML = newForm.innerHTML.replaceAll(`-${currentFormCount - 1}-`, `-${currentFormCount}-`);
//         newForm.innerHTML = newForm.innerHTML.replaceAll(`_${currentFormCount - 1}`, `_${currentFormCount}`);

//         formsetContainer.appendChild(newForm);
//         totalForms.value = currentFormCount + 1;

//         // aplicarSelect2();
//         actualizarOpcionesDisponibles();
//         attachRemoveButtons(); // asegurar que el nuevo botón funcione
//     });

//     attachRemoveButtons();

//     // 🔴 Validación duplicados antes de enviar
//     document.querySelector('form').addEventListener('submit', function (e) {
//         const selects = formsetContainer.querySelectorAll(`select[name^="${prefix}"]`);
//         const valores = [];
//         let duplicado = false;

//         selects.forEach(select => {
//             const val = select.value;
//             if(val){
//                 if(valores.includes(val)){
//                     duplicado = true;
//                 } else {
//                     valores.push(val);
//                 }
//             }
//         });

//         if(duplicado){
//             e.preventDefault();
//             alert("No puedes seleccionar el mismo producto más de una vez.");
//         }
//     });

//     // Ejecutar al cargar la página
//     actualizarOpcionesDisponibles();
// });

// document.addEventListener("DOMContentLoaded", () => {
//     const container = document.getElementById("formset-container");
//     const prefix = container.dataset.prefix;
//     const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
//     const emptyForm = container.dataset.emptyForm;

//     // Agregar nuevo formulario
//     document.getElementById("add-form").addEventListener("click", () => {
//         let totalForms = parseInt(totalFormsInput.value);
//         let newFormHtml = emptyForm.replace(/__prefix__/g, totalForms);
//         let div = document.createElement("div");
//         div.classList.add("formset-item", "border", "p-3", "mb-2", "bg-light", "rounded");
//         div.innerHTML = newFormHtml;

//         div.querySelector(".remove-form").addEventListener("click", e => {
//             div.remove();
//             totalFormsInput.value = parseInt(totalFormsInput.value) - 1; // Solo decrementa TOTAL_FORMS para formularios nuevos
//         });

//         container.appendChild(div);
//         totalFormsInput.value = totalForms + 1;
//     });

//     // Manejar "Quitar" para todos los formularios
//     container.querySelectorAll(".remove-form").forEach(btn => {
//         btn.addEventListener("click", e => {
//             const formItem = e.target.closest(".formset-item");
//             const deleteInput = formItem.querySelector(`input[name$='-DELETE']`);

//             if (deleteInput) {
//                 // Formularios existentes: marcar DELETE y ocultar
//                 deleteInput.checked = true;
//                 formItem.style.display = 'none';
//             } else {
//                 // Formularios nuevos: eliminar del DOM y decrementar TOTAL_FORMS
//                 formItem.remove();
//                 totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
//             }
//         });
//     });
// });

// function attachRemoveButtons() {
//     formsetContainer.querySelectorAll(".remove-form").forEach(btn => {
//         btn.onclick = function() {

//             const formItem = btn.closest(".formset-item");

//             // 1️⃣ Busca el checkbox DELETE generado por Django para este formulario
//             const deleteCheckbox = formItem.querySelector('input[name$="-DELETE"]');

//             if (deleteCheckbox) {
//                 // 2️⃣ Marca el checkbox para que Django lo elimine al guardar
//                 deleteCheckbox.checked = true;

//                 // 3️⃣ ❗ No borres el nodo, solo ocúltalo para que el formset lo procese
//                 formItem.style.display = 'none';
//             } else {
//                 // 🔄 Si es un formulario recién creado (sin DELETE), podemos eliminarlo del DOM
//                 formItem.remove();

//                 // 4️⃣ Renumera los formularios restantes
//                 const items = formsetContainer.querySelectorAll('.formset-item');
//                 items.forEach((item, index) => {
//                     item.querySelectorAll('input, select, textarea').forEach(field => {
//                         if (field.name) {
//                             field.name = field.name.replace(/\-\d+\-/, '-' + index + '-');
//                             field.id = 'id_' + field.name;
//                         }
//                     });
//                 });

//                 // 5️⃣ Actualiza el contador TOTAL_FORMS para los formularios nuevos
//                 totalForms.value = items.length;

//                 // 6️⃣ Vuelve a actualizar opciones dinámicas si aplica
//                 actualizarOpcionesDisponibles();
//             }
//         };
//     });
// }

$(document).ready(function () {
    console.log("Lista grupos");

    // ==========================
    // Inicialización de DataTable
    // ==========================
    const table = $('#tabla-grupos').DataTable({
        columnDefs: [
            { className: "text-center", targets: [0, 1, 2, 3] },
            { orderable: false, targets: [2, 3] },
            { searchable: false, targets: [3] }
        ],
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
            paginate: { first: "Primero", last: "Último", next: "Siguiente", previous: "Anterior" },
            aria: { sortAscending: ": Activar para ordenar de forma ascendente", sortDescending: ": Activar para ordenar de forma descendente" },
            buttons: { colvis: "Visibilidad" }
        },
        initComplete: function () {
            const api = this.api();
            api.rows().every(function () {
                const tr = $(this.node());
                const detalle = tr.data('detalle');
                if (detalle) {
                    this.child(detalle).show();
                    tr.addClass('shown');
                }
            });
        }
    });

    // Expandir/cerrar detalles
    $('#tabla-grupos tbody').on('click', 'td.dt-control', function () {
        const tr = $(this).closest('tr');
        const row = table.row(tr);
        if (row.child.isShown()) {
            row.child.hide();
            tr.removeClass('shown');
        } else {
            const detalle = tr.data('detalle');
            row.child(detalle).show();
            tr.addClass('shown');
        }
    });

    // ==========================
    // Configuración de formset
    // ==========================
    const formsetContainer = document.getElementById('formset-container');
    if (!formsetContainer) return; // Previene errores si no existe
    const prefix = formsetContainer.dataset.prefix;
    const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    const addFormButton = document.getElementById('add-form');

    // --------------------------
    // Función: aplicar Select2
    // --------------------------
    function aplicarSelect2() {
        console.log("Aplicando Select2...");
        $('select:not(.swal2-select, .modal select, [data-no-select2])').each(function() {
            if (!$(this).data('select2')) {
                $(this).select2({
                    width: '100%',
                    theme: 'classic',
                    placeholder: "Seleccione una opción",
                    allowClear: true
                });
            }
        });
    }

    aplicarSelect2();

    // --------------------------
    // Función: actualizar opciones únicas
    // --------------------------
    function actualizarOpcionesDisponibles() {
        const selects = formsetContainer.querySelectorAll(`select[name^="${prefix}"]`);
        const seleccionadas = new Set();
        selects.forEach(sel => { if (sel.value) seleccionadas.add(sel.value); });

        selects.forEach(sel => {
            [...sel.options].forEach(opt => {
                opt.disabled = !(opt.value === "" || opt.value === sel.value || !seleccionadas.has(opt.value));
            });
            $(sel).trigger('change.select2');
        });
    }

    // --------------------------
    // Agregar nueva fila
    // --------------------------
    addFormButton.addEventListener('click', () => {
        const currentFormCount = parseInt(totalForms.value);
        const lastForm = formsetContainer.querySelector('.formset-item:last-of-type');
        if (!lastForm) return console.warn("No hay formulario base para clonar");

        // Destruir select2 si existe
        $(lastForm).find('select').each(function() {
            if ($.fn.select2 && $(this).data('select2')) {
                $(this).select2('destroy');
            }
        });

        const newForm = lastForm.cloneNode(true);
        newForm.querySelectorAll('input, select, textarea').forEach(field => {
            if (field.tagName === 'SELECT') field.selectedIndex = 0;
            else field.value = '';
        });

        // Renumerar índices
        if (newForm.innerHTML) {
            newForm.innerHTML = newForm.innerHTML
                .replaceAll(`-${currentFormCount - 1}-`, `-${currentFormCount}-`)
                .replaceAll(`_${currentFormCount - 1}`, `_${currentFormCount}`);
        }

        formsetContainer.appendChild(newForm);
        totalForms.value = currentFormCount + 1;

        aplicarSelect2();
        actualizarOpcionesDisponibles();
        attachRemoveButtons();
    });

    // --------------------------
    // Función: remover formulario
    // --------------------------
    function attachRemoveButtons() {
        formsetContainer.querySelectorAll(".remove-form").forEach(btn => {
            btn.onclick = function() {
                const formItem = btn.closest(".formset-item");
                const deleteCheckbox = formItem.querySelector('input[name$="-DELETE"]');

                if (deleteCheckbox) {
                    deleteCheckbox.checked = true;
                    formItem.style.display = 'none';
                } else {
                    formItem.remove();
                    const items = formsetContainer.querySelectorAll('.formset-item');
                    items.forEach((item, index) => {
                        item.querySelectorAll('input, select, textarea').forEach(field => {
                            if (field.name) {
                                field.name = field.name.replace(/\-\d+\-/, '-' + index + '-');
                                field.id = 'id_' + field.name;
                            }
                        });
                    });
                    totalForms.value = items.length;
                    actualizarOpcionesDisponibles();
                }
            };
        });
    }

    attachRemoveButtons();

    // --------------------------
    // Validar duplicados
    // --------------------------
    document.querySelector('form').addEventListener('submit', function (e) {
        const selects = formsetContainer.querySelectorAll(`select[name^="${prefix}"]`);
        const valores = [];
        let duplicado = false;

        selects.forEach(select => {
            const val = select.value;
            if (val) {
                if (valores.includes(val)) duplicado = true;
                else valores.push(val);
            }
        });

        if (duplicado) {
            e.preventDefault();
            alert("⚠️ No puedes seleccionar el mismo producto más de una vez.");
        }
    });

    actualizarOpcionesDisponibles();
});
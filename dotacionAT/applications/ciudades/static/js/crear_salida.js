// document.querySelector('form').addEventListener('submit', function(e) {
//     console.log("Proveedor:", document.querySelector('input[name="proveedor"]').value);
//     console.log("Productos:", [...document.querySelectorAll('input[name="productos[]"]')].map(i => i.value));
//     console.log("Cantidades:", [...document.querySelectorAll('input[name="cantidades[]"]')].map(i => i.value));
//     console.log("Precios:", [...document.querySelectorAll('input[name="precios[]"]')].map(i => i.value));
//     console.log("Total:", document.getElementById('inputTotalOrden').value);
// });


console.log("Hola Crear Salida");


var dataTableClienteSalida;
var dataTableProductos;

var proveedoresInitialized = false;
var productosInitialized = false;

const dataTableOptions = {
    columnDefs: [
        { className: "text-center", targets: "_all" },
        { orderable: false, targets: -1 }
    ],
    pageLength: 1,
    destroy: true,
    language: {
        processing: "Procesando...",
        lengthMenu: "Mostrar _MENU_ registros",
        zeroRecords: "No se encontraron resultados",
        emptyTable: "Ningún dato disponible en esta tabla",
        info: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_",
        infoEmpty: "Mostrando 0 de 0 registros",
        infoFiltered: "(filtrado de un total de _MAX_ registros)",
        search: "Buscar:",
        paginate: {
            first: "Primero",
            last: "Último",
            next: "Siguiente",
            previous: "Anterior"
        },
    },
    lengthChange: false,
};

// ✅ Tabla de Proveedores
const initDataTableClienteSalida = async () => {
    if (proveedoresInitialized) {
        dataTableClienteSalida.destroy();
    }

    await cargarProveedores();

    const table = document.getElementById('tablaClienteEntrega');
    if (table) {
        dataTableClienteSalida = $('#tablaClienteEntrega').DataTable(dataTableOptions);
        proveedoresInitialized = true;
    }
};

const cargarProveedores = async () => {
    try {
        const response = await fetch('/list_clientes/');
        const data = await response.json();
        const tableBody = document.getElementById('tableBody_clienteOrden');

        if (tableBody) {
            let content = ``;

            data.cliente.forEach(proveedor => {
               
                content += `
                    <tr>
                        <td>${proveedor.id_cliente}</td>
                        <td>${proveedor.nombre}</td>
                        <td>
                            <button type="button" class="btn btn-sm btn-primary"
                                onclick="seleccionarProveedor('${proveedor.id_cliente}', '${proveedor.nombre}', '${proveedor.id_ciudad}', '${proveedor.telefono}')">
                                Seleccionar
                            </button>
                        </td>
                    </tr>
                `;
            });

            tableBody.innerHTML = content;
        }

    } catch (error) {
        console.error("Error al cargar proveedores:", error);
    }
};

// function seleccionarProveedor(id, nombre) {
//     // Setear valores ocultos
//     document.getElementById('listaProveedor').value = id;

//     // Insertar nombre visualmente en el div
//     const divProveedor = document.querySelector('.nuevoProveedor');
//     divProveedor.innerHTML = `
//         <label class="col-sm-4 col-form-label">Proveedor seleccionado:</label>
//         <div class="col-sm-8">
//             <input type="text" class="form-control" value="${nombre}" readonly>
//         </div>
//     `;
// }

function seleccionarProveedor(id, nombre, ciudad, telefono) {
    // Prevenir múltiples selecciones
    const tbody = document.querySelector("#proveedorSeleccionado tbody");
    tbody.innerHTML = ''; // Limpiar contenido anterior

    const fila = document.createElement("tr");
    fila.setAttribute("data-id", id);
    fila.innerHTML = `
        <td>${nombre}<input type="hidden" name="proveedor" value="${id}"></td>
        <td>${ciudad}<input type="hidden" value="${ciudad}"></td>
        <td>${telefono}<input type="hidden" value="${telefono}"></td>
        <td>
            <button type="button" class="btn btn-danger btn-sm" onclick="quitarProveedor()">
                <i class="fa fa-times"></i>
            </button>
        </td>
    `;
    tbody.appendChild(fila);

     // Mostrar el select condicional
if(nombre === 'Atiempo SAS'){

    document.getElementById("bodegaDestinoContainer").style.display = "block";

    const bodegaSelect = document.getElementById("selectBodegaEntrada");
    
    // Verifica si el campo es visible
    const visible = bodegaSelect.offsetParent !== null;

    if (visible) {
        bodegaSelect.setAttribute("required", "required");
    } 
    

}



}

function quitarProveedor() {
    const tbody = document.querySelector("#proveedorSeleccionado tbody");
    tbody.innerHTML = '';
    document.getElementById('listaCliente').value = ''; // limpiar input oculto



    document.getElementById("bodegaDestinoContainer").style.display = "none";

}


const dataTableOptionsOrden = {
    columnDefs: [
        { className: "text-center", targets: "_all" },
        { orderable: false, targets: -1 }
    ],
    pageLength: 10,
    destroy: true,
    language: {
        processing: "Procesando...",
        lengthMenu: "Mostrar _MENU_ registros",
        zeroRecords: "No se encontraron resultados",
        emptyTable: "Ningún dato disponible en esta tabla",
        info: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_",
        infoEmpty: "Mostrando 0 de 0 registros",
        infoFiltered: "(filtrado de un total de _MAX_ registros)",
        search: "Buscar:"   
    },
    paging: false,
    info: false,
};




// ✅ Tabla de Productos
// const initDataTableProductos = async () => {
//     if (productosInitialized) {
//         dataTableProductos.destroy();
//     }

//     await cargarProductos();

//     const table = document.getElementById('datatableProductosOrden');
//     if (table) {
//         dataTableProductos = $('#datatableProductosOrden').DataTable(dataTableOptionsOrden);
//         productosInitialized = true;
//     }
// };

// const cargarProductos = async () => {
//     try {
//         const response = await fetch('/inventario_bodega_json/');
//         const data = await response.json();
//         const tableBody = document.getElementById('tableBody_productosOrden');

//         if (tableBody) {
//             let content = ``;
//             data.inventarios.forEach(producto => {
//                 const activo = producto.activo === "True" || producto.activo === true;
//                 content += `
//                     <tr class="text-center">
//                         <td>${producto.id_producto}</td>
//                         <td>${producto.nombre}</td>
//                         <td>
                            
//                                   <button class="btn btn-sm btn-primary" onclick="agregarProductoAOrden('${producto.id_producto}', '${producto.nombre}', '0')">
//         Agregar
//     </button>
//                         </td>
//                     </tr>
//                 `;
//             });
//             tableBody.innerHTML = content;
//         }

//     } catch (error) {
//         alert("Error al obtener productos.");
//         console.error("Error al obtener productos:", error);
//     }
// };


$(document).ready(function() {
    // Cargar productos inicialmente si ya hay una bodega seleccionada
  

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



    // Ejecutar al cambiar el select de bodega
$('#selectBodegaSalida').on('change', function() {
        
console.log("Hola");


const cargarProductos = async () => {
    try {
        const filtroBodega = document.getElementById('selectBodegaSalida').value;

        const response = await fetch('/inventario_bodega_json/');
        const data = await response.json();
        const tableBody = document.getElementById('tableBody_productosOrden');

        if (tableBody) {
            // Destruye el DataTable si ya está inicializado
            if ($.fn.DataTable.isDataTable('#datatableProductosOrden')) {
                $('#datatableProductosOrden').DataTable().destroy();
            }

    let content = ``;
const inventariosFiltrados = filtroBodega
    ? data.inventarios.filter(p => p.bodega_id == filtroBodega)
    : data.inventarios;

inventariosFiltrados.forEach(producto => {
    let colorClass = '';

    if (producto.stock < 10) {
        colorClass = 'bg-danger text-white fw-bold rounded px-2 py-1'; // rojo
    } else if (producto.stock < 20) {
        colorClass = 'bg-warning-custom'; // naranja
    } else {
        colorClass = 'bg-success text-white fw-bold rounded px-2 py-1'; // verde
    }

    

    content += `
        <tr class="text-center">
            <td>${producto.id_producto}</td>
            <td>${producto.producto}</td>
            <td><span class="${colorClass}">${producto.stock}</span></td>
             <td>
                ${producto.stock > 0
                    ? `<button class="btn btn-sm btn-primary" onclick="agregarProductoAOrden('${producto.id_producto}', '${producto.producto}', '${producto.stock}')">
                        Agregar
                       </button>`
                    : `<span class="text-muted">Sin stock</span>`
                }
            </td>
        </tr>
    `;
});

            tableBody.innerHTML = content;

            // Reinicializa el DataTable
            $('#datatableProductosOrden').DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.5/i18n/es-ES.json'
                }
            });
        }

    } catch (error) {
        alert("Error al obtener productos.");
        console.error("Error al obtener productos:", error);
    }
}


    // 👉 Llamada a la función que definiste arriba
    cargarProductos()
    })
})



// ✅ Llamamos ambas al cargar la página
window.addEventListener("load", async () => {
    await initDataTableClienteSalida();
    // await initDataTableProductos();
    console.log("Página cargada");
});


let productosAgregados = [];

function agregarProductoAOrden(id, nombre, stock) {
    // Evitar duplicados
    if (productosAgregados.includes(id)) {
        alert("Este producto ya ha sido agregado.");
        return;
    }

    productosAgregados.push(id);

    const tbody = document.querySelector("#productosSeleccionados tbody");
    const fila = document.createElement("tr");
    fila.setAttribute("data-id", id);

    fila.innerHTML = `
        <td>${nombre}<input type="hidden" name="productosNew[]" value="${id}"></td>
        <td>
            <input type="text" name="cantidades[]" class="form-control text-center cantidad" value="1" onchange="cambiarCantidad(this)"  min="0" step="0.01" required>
            <input type="hidden" class="stock-hidden" value="${stock}"></td>      
        <td>
            <button type="button" class="btn btn-danger btn-sm" onclick="quitarProducto(${id}, this)">
                <i class="fa fa-times"></i>
            </button>
        </td>
    `;
    tbody.appendChild(fila);
    
    console.log(typeof $.fn.number);
    
    // $(fila).find(".valorUnitario").number(true, 2);
    // $(fila).find(".cantidad").number(true);
    // $(fila).find(".subtotal").number(true, 2);
    
    // actualizarSubtotal(fila); 
    // actualizarTotalGeneral();
    // calcular subtotal inicial
    //formatNumber()
    cambiarCantidad()
}


//   <td class="subtotal text-right">0.00</td>
//<td><input type="text" name="precios[]" class="form-control text-right valorUnitario"   
// onchange="actualizarSubtotal(this)" value="${costo}"  required></td>


function formatNumberInput(inputElement) {
    let value = parseFloat(inputElement.value);
    if (!isNaN(value) && value >= 0) {
        inputElement.value = new Intl.NumberFormat('es-CO', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    } else {
        inputElement.value = '';
    }
}

function quitarProducto(id, btn) {
    productosAgregados = productosAgregados.filter(pid => pid != id);
    btn.closest("tr").remove();

    actualizarTotalGeneral();
}

// function actualizarSubtotal(elemento) {
//     const fila = elemento.closest("tr");
//     const cantidad = parseFloat(fila.querySelector('input[name="cantidades[]"]').value) || 0;
//      console.log("Tipo:", typeof cantidad);
//     const precio = parseFloat(fila.querySelector('input[name="precios[]"]').value) || 0;
//     console.log("Tipo:", typeof precio);
//     const subtotal = (cantidad * precio);
//     fila.querySelector(".subtotal").innerText = subtotal;

//     console.log(cantidad);
//     console.log(precio);
//     console.log(subtotal);
    
// }


function parsePrecioColombiano(valorRaw) {
    const soloNumeros = valorRaw.replace(/[^0-9.,]/g, '');  // limpia símbolos
    const tieneComaDecimal = soloNumeros.includes(',');
    const tienePuntoDecimal = soloNumeros.includes('.');

    // Caso 1: Formato colombiano: 12.500,00
    if (tieneComaDecimal && tienePuntoDecimal && soloNumeros.indexOf(',') > soloNumeros.indexOf('.')) {
        return parseFloat(soloNumeros.replace(/\./g, '').replace(',', '.'));
    }

    // Caso 2: Formato americano: 12,500.00
    if (tieneComaDecimal && tienePuntoDecimal && soloNumeros.indexOf('.') > soloNumeros.indexOf(',')) {
        return parseFloat(soloNumeros.replace(/,/g, ''));
    }

    // Caso 3: Solo coma (12,50) → 12.50
    if (!tienePuntoDecimal && tieneComaDecimal) {
        return parseFloat(soloNumeros.replace(',', '.'));
    }

    // Caso 4: Solo punto o número limpio
    return parseFloat(soloNumeros);
}


function actualizarSubtotal(input) {
    const fila = input.closest('tr');

    const cantidad = parseFloat(fila.querySelector('input[name="cantidades[]"]').value) || 0;

    const inputPrecio = fila.querySelector('input[name="precios[]"]');
    const raw = inputPrecio.value.trim();
    const precio = parsePrecioColombiano(raw) || 0;  // Solo convierte coma decimal
    // const precio = parseFloat(clean) || 0;
    const subtotal = cantidad * precio;

    fila.querySelector('.subtotal').textContent = subtotal.toLocaleString('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 2
    });

//     console.log(cantidad);
//     console.log("Raw:", raw);      // Lo que ve el usuario
// console.log("Clean:", clean);  // Lo que se va a parsear
// console.log("Precio:", precio);


    console.log(subtotal);

    // actualizarTotalGeneral();
    
}




function agregarProveedorAOrden(id, nombre) {
    // Evitar duplicados
    if (productosAgregados.includes(id)) {
        alert("Este proveedor ya ha sido agregado.");
        return;
    }

    productosAgregados.push(id);

    const tbody = document.querySelector("#proveedorSeleccionados tbody");
    const fila = document.createElement("tr");
    fila.setAttribute("data-id", id);

    fila.innerHTML = `
        <td>${nombre}<input type="hidden" name="proveedor[]" value="${id}"></td>
        <td>${proveedor.id_ciudad}</td>
        <td>${proveedor.telefono}</td>
        <td>
            <button type="button" class="btn btn-danger btn-sm" onclick="quitarProducto(${id}, this)">
                <i class="fa fa-times"></i>
            </button>
        </td>
    `;


    tbody.appendChild(fila);
    
}

function actualizarTotalGeneral() {
    let total = 0;
    document.querySelectorAll('#productosSeleccionados tbody tr').forEach(fila => {
        const subtotalTexto = fila.querySelector('.subtotal').textContent;
        const subtotalNum = parsePrecioColombiano(subtotalTexto) || 0;
        total += subtotalNum;
    });

    const totalFormateado = total.toLocaleString('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 2
    });

    document.getElementById('totalOrden').textContent = totalFormateado;

    // Actualizar el campo oculto para enviar al backend
    document.getElementById('inputTotalOrden').value = total.toFixed(2); // Valor limpio, sin formato
}

// function validarCantidad(input) {
//     input.value = input.value.replace(/[^0-9]/g, ''); // solo números enteros positivos
//     if (input.value === '' || parseInt(input.value) < 1) {
//         input.value = 1;
//     }
// }

// function validarPrecio(input) {
//     // Elimina caracteres no permitidos excepto el punto
//     input.value = input.value.replace(/[^0-9.]/g, '');

//     // Limita a 2 decimales
//     let valor = parseFloat(input.value);
//     if (isNaN(valor) || valor < 0) {
//         input.value = '00000000.00';
//     } else {
//         input.value = valor.toFixed(2);
//     }
// }

document.querySelector('form').addEventListener('submit', function() {
    document.querySelectorAll('input[name="precios[]"]').forEach(input => {
        input.value = input.value.replace(/,/g, '');
    });
});
   

$(document).ready(function() {
    $('#selectBodegaSalida').select2({
        placeholder: 'Bodega Salida',
        allowClear: true,
        width: '100%'
    });
      $('#selectBodegaEntrada').select2({
        placeholder: 'Bodega Entrada',
        allowClear: true,
        width: '100%'
    });

});



document.addEventListener('DOMContentLoaded', function () {
    fetch('/list_bodegas/')
    .then(response => response.json())
    .then(data => {
        const select = document.getElementById('selectBodegaSalida');
        select.innerHTML = '<option value="">Bodega Salida</option>';

        data.bodegas.forEach(bodega => {  // <-- ¡Aquí va data.bodegas!
            const option = document.createElement('option');
            option.value = bodega.id_bodega;
            option.textContent = bodega.nombre + ' - ' + bodega.ciudad;
            select.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error al cargar las bodegas:', error);
        const select = document.getElementById('selectBodegaSalida');
        select.innerHTML = '<option value="">Error al cargar</option>';
    })
});

document.addEventListener('DOMContentLoaded', function () {
    fetch('/list_bodegas/')
    .then(response => response.json())
    .then(data => {
        const select = document.getElementById('selectBodegaEntrada');
        select.innerHTML = '<option value="">Bodega Entrega</option>';

        data.bodegas.forEach(bodega => {  // <-- ¡Aquí va data.bodegas!
            const option = document.createElement('option');
            option.value = bodega.id_bodega;
            option.textContent = bodega.nombre + ' - ' + bodega.ciudad;
            select.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error al cargar las bodegas:', error);
        const select = document.getElementById('selectBodegaEntrada');
        select.innerHTML = '<option value="">Error al cargar</option>';
    })
});




function cambiarCantidad(input) {
    const fila = input.closest('tr'); // Encuentra la fila donde está el input
    const stockInput = fila.querySelector('.stock-hidden'); // Encuentra el input hidden con el stock
    const stock = parseFloat(stockInput.value); // Stock disponible
    const cantidad = parseFloat(input.value); // Cantidad digitada

    if (cantidad > stock) {
        Swal.fire({
            icon: 'error',
            title: 'Cantidad excedida',
            text: `La cantidad ingresada (${cantidad}) excede el stock disponible (${stock}).`,
            confirmButtonText: 'Aceptar'
        }).then(() => {
            // Opciones:
            // 1. Eliminar la fila:
            // fila.remove();

            // 2. O simplemente volver a poner 1 como valor válido:
            input.value = 1;
        });
    }
}



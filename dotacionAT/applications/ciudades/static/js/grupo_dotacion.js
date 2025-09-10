document.addEventListener('DOMContentLoaded', () => {

  function aplicarSelect2() {
    $('select').select2({
      width: '100%',
      theme: 'classic',
      placeholder: "Seleccione una opción",
      allowClear: true
    });
  }

  $(document).ready(function () {
  $('select.select2').select2({
    width: '100%',
    theme: 'classic',
    placeholder: 'Seleccione una o varias opciones',
    allowClear: true
    });
  });

  aplicarSelect2();

  const formsetContainer = document.getElementById('formset-container');
  const addFormButton = document.getElementById('add-form');
  const totalForms = document.getElementById('id_productos-TOTAL_FORMS');

  // 🟢 Ocultar productos ya seleccionados
  function actualizarOpcionesDisponibles() {
    const selects = document.querySelectorAll('select[name^="productos-"][name$="-producto"]');

    // Obtiene todos los valores seleccionados
    const valoresSeleccionados = Array.from(selects).map(s => s.value).filter(v => v !== "");

    selects.forEach(select => {
      const selectedValue = select.value;

      // Iteramos sobre cada opción
      $(select).find('option').each(function () {
        const optionValue = this.value;

        // Mostrar la opción si no está seleccionada en otro campo
        if (
          optionValue === "" || // opción vacía
          optionValue === selectedValue || // opción actual del campo
          !valoresSeleccionados.includes(optionValue)
        ) {
          $(this).prop('disabled', false);
        } else {
          $(this).prop('disabled', true);
        }
      });

      // 🔁 Refrescar Select2
      $(select).trigger('change.select2');
    });
  }

  // 🟡 Al cambiar cualquier select, refrescamos opciones disponibles
  document.addEventListener('change', e => {
    if (e.target.matches('select[name^="productos-"][name$="-producto"]')) {
      actualizarOpcionesDisponibles();
    }
  });

  // ➕ Agregar nueva fila
  addFormButton.addEventListener('click', () => {
    const currentFormCount = parseInt(totalForms.value);
    const lastForm = formsetContainer.querySelector('.formset-item:last-of-type');

    $(lastForm).find('select').select2('destroy');

    const newForm = lastForm.cloneNode(true);

    // Limpiar valores del clon
    newForm.querySelectorAll('input, select').forEach(input => {
      input.value = '';
    });

    // Actualizar índices
    newForm.innerHTML = newForm.innerHTML.replaceAll(`-${currentFormCount - 1}-`, `-${currentFormCount}-`);
    newForm.innerHTML = newForm.innerHTML.replaceAll(`_${currentFormCount - 1}`, `_${currentFormCount}`);

    formsetContainer.appendChild(newForm);
    totalForms.value = currentFormCount + 1;

    aplicarSelect2();
    actualizarOpcionesDisponibles();
  });

  // 🔴 Validar duplicados antes del submit
  document.querySelector('form').addEventListener('submit', function (e) {
    const selects = document.querySelectorAll('select[name^="productos-"][name$="-producto"]');
    const valores = [];
    let duplicado = false;

    selects.forEach(select => {
      const val = select.value;
      if (val) {
        if (valores.includes(val)) {
          duplicado = true;
        } else {
          valores.push(val);
        }
      }
    });

    if (duplicado) {
      e.preventDefault();
      alert("No puedes seleccionar el mismo producto más de una vez.");
    }
  });

  // Ejecutar en el primer renderizado
  actualizarOpcionesDisponibles();
});

document.addEventListener("DOMContentLoaded", function() {
    let formsetContainer = document.getElementById("formset-container");
    let addButton = document.getElementById("add-form");

    // Total forms de Django (oculto en el management_form)
    let totalForms = document.getElementById("id_" + "{{ formset.prefix }}" + "-TOTAL_FORMS");

    // 👉 Agregar producto
    addButton.addEventListener("click", function() {
        let formIndex = totalForms.value;
        let emptyForm = formsetContainer.querySelector(".formset-item").cloneNode(true);

        // Limpiar valores de inputs en el clon
        emptyForm.querySelectorAll("input, select").forEach(el => {
            el.value = "";
            if (el.type === "checkbox") el.checked = false;
        });

        // Reemplazar índices __prefix__ con el nuevo index
        emptyForm.innerHTML = emptyForm.innerHTML.replaceAll(
            new RegExp(`-${formIndex - 1}-`, "g"),
            `-${formIndex}-`
        );

        formsetContainer.appendChild(emptyForm);
        totalForms.value = parseInt(formIndex) + 1;

        attachRemoveButtons();
    });

    // 👉 Quitar producto
    function attachRemoveButtons() {
        document.querySelectorAll(".remove-form").forEach(btn => {
            btn.onclick = function() {
                btn.closest(".formset-item").remove();
                // Actualizar TOTAL_FORMS
                let items = document.querySelectorAll(".formset-item").length;
                totalForms.value = items;
            };
        });
    }

    // Inicializar
    attachRemoveButtons();
});
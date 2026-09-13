/**
 * DROPDOWNS.JS
 * ============================================================================
 * Propósito: Gestionar dropdowns, selects dinámicos y menús desplegables
 * ============================================================================
 */

const Dropdowns = {
  /**
   * CREAR SELECT CON OPCIONES
   */
  crearSelect: function(id, opciones, seleccionada = null) {
    const select = document.createElement('select');
    select.id = id;
    select.className = 'form-select';

    opciones.forEach(opcion => {
      const option = document.createElement('option');
      option.value = opcion.valor || opcion;
      option.textContent = opcion.texto || opcion;
      if (opcion.valor === seleccionada || opcion === seleccionada) {
        option.selected = true;
      }
      select.appendChild(option);
    });

    return select;
  },

  /**
   * LLENAR SELECT CON DATOS
   */
  llenarSelect: function(idSelect, datos, campo_valor = 'id', campo_texto = 'nombre') {
    const select = document.getElementById(idSelect);
    if (!select) return;

    select.innerHTML = '<option value="">-- Seleccionar --</option>';

    datos.forEach(item => {
      const option = document.createElement('option');
      option.value = item[campo_valor];
      option.textContent = item[campo_texto];
      select.appendChild(option);
    });
  },

  /**
   * OBTENER VALOR SELECCIONADO
   */
  obtenerSeleccionado: function(idSelect) {
    const select = document.getElementById(idSelect);
    return select ? select.value : null;
  },

  /**
   * ESTABLECER VALOR SELECCIONADO
   */
  establecerSeleccionado: function(idSelect, valor) {
    const select = document.getElementById(idSelect);
    if (select) {
      select.value = valor;
    }
  },

  /**
   * DESHABILITAR/HABILITAR SELECT
   */
  habilitarSelect: function(idSelect, habilitado = true) {
    const select = document.getElementById(idSelect);
    if (select) {
      select.disabled = !habilitado;
    }
  },

  /**
   * DROPDOWN MENU PERSONALIZADO
   */
  crearMenu: function(id, titulo, items) {
    const div = document.createElement('div');
    div.className = 'dropdown';
    div.innerHTML = `
      <button class="btn btn-secondary dropdown-toggle" type="button" id="${id}" data-bs-toggle="dropdown">
        ${titulo}
      </button>
      <ul class="dropdown-menu" aria-labelledby="${id}">
        ${items.map((item, index) => `
          <li>
            <a class="dropdown-item" href="#" data-action="${item.id || index}">
              ${item.texto}
            </a>
          </li>
        `).join('')}
      </ul>
    `;
    return div;
  },

  /**
   * AGREGAR EVENTOS A ITEMS DE DROPDOWN
   */
  enClickDropdown: function(idDropdown, callback) {
    const dropdown = document.getElementById(idDropdown);
    if (!dropdown) return;

    const items = dropdown.nextElementSibling?.querySelectorAll('.dropdown-item');
    items?.forEach(item => {
      item.addEventListener('click', function(e) {
        e.preventDefault();
        const action = this.getAttribute('data-action');
        callback(action, this);
      });
    });
  },

  /**
   * FILTRAR SELECT POR BÚSQUEDA
   */
  filtrarSelect: function(idSelect, termino) {
    const select = document.getElementById(idSelect);
    if (!select) return;

    const options = select.querySelectorAll('option');
    let encontrados = 0;

    options.forEach(option => {
      if (option.value === '') return; // Omitir placeholder

      const coincide = option.textContent.toLowerCase().includes(termino.toLowerCase());
      option.style.display = coincide ? '' : 'none';

      if (coincide) encontrados++;
    });

    return encontrados;
  },

  /**
   * MULTI-SELECT (CHECKBOXES)
   */
  crearMultiSelect: function(id, opciones) {
    const div = document.createElement('div');
    div.id = id;
    div.className = 'multi-select';

    opciones.forEach((opcion, index) => {
      const label = document.createElement('label');
      label.className = 'form-check-label';

      const input = document.createElement('input');
      input.type = 'checkbox';
      input.className = 'form-check-input';
      input.value = opcion.valor || opcion;
      input.name = `${id}_${index}`;

      label.appendChild(input);
      label.appendChild(document.createTextNode(opcion.texto || opcion));

      div.appendChild(label);
      div.appendChild(document.createElement('br'));
    });

    return div;
  },

  /**
   * OBTENER VALORES SELECCIONADOS EN MULTI-SELECT
   */
  obtenerMultiSeleccionado: function(id) {
    const div = document.getElementById(id);
    if (!div) return [];

    const checkboxes = div.querySelectorAll('input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
  },

  /**
   * CASCADA DE SELECTS (Dependientes)
   */
  configurarCascada: function(selectPadre, selectHijo, datos) {
    const parentSelect = document.getElementById(selectPadre);
    const childSelect = document.getElementById(selectHijo);

    if (!parentSelect || !childSelect) return;

    parentSelect.addEventListener('change', function() {
      const selectedValue = this.value;
      const children = datos[selectedValue] || [];
      this.llenarSelect(selectHijo, children, 'id', 'nombre');
    });
  },

  /**
   * BUSQUEDA EN SELECT (AUTOCOMPLETE)
   */
  habilitarBusqueda: function(idSelect) {
    const select = document.getElementById(idSelect);
    if (!select) return;

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control mb-2';
    input.placeholder = 'Buscar...';

    input.addEventListener('input', function() {
      const termino = this.value.toLowerCase();
      const options = select.querySelectorAll('option');

      options.forEach(option => {
        if (option.value === '') return;
        const coincide = option.textContent.toLowerCase().includes(termino);
        option.style.display = coincide ? '' : 'none';
      });
    });

    select.parentNode.insertBefore(input, select);
  },

  /**
   * VACIAR SELECT
   */
  vaciarSelect: function(idSelect) {
    const select = document.getElementById(idSelect);
    if (select) {
      select.innerHTML = '<option value="">-- Seleccionar --</option>';
    }
  },

  /**
   * DESHABILITAR OPCIÓN EN SELECT
   */
  deshabilitarOpcion: function(idSelect, valor) {
    const select = document.getElementById(idSelect);
    if (!select) return;

    const option = select.querySelector(`option[value="${valor}"]`);
    if (option) {
      option.disabled = true;
    }
  },

  /**
   * HABILITAR OPCIÓN EN SELECT
   */
  habilitarOpcion: function(idSelect, valor) {
    const select = document.getElementById(idSelect);
    if (!select) return;

    const option = select.querySelector(`option[value="${valor}"]`);
    if (option) {
      option.disabled = false;
    }
  },
};

// EXPORT para CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Dropdowns;
}
window.Dropdowns = Dropdowns;

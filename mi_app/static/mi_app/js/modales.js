/**
 * MODALES.JS
 * ============================================================================
 * Propósito: Gestionar modales (crear, abrir, cerrar, validar)
 * ============================================================================
 */

const Modales = {
  /**
   * CREAR MODAL
   */
  crearModal: function(id, titulo, contenido, botones = []) {
    const modal = document.createElement('div');
    modal.id = id;
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');
    modal.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">${titulo}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            ${contenido}
          </div>
          <div class="modal-footer">
            ${botones.length > 0 ? botones.map(btn => 
              `<button type="button" class="btn btn-${btn.tipo || 'secondary'}" ${btn.atributos || ''}>
                ${btn.texto}
              </button>`
            ).join('') : ''}
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    return new bootstrap.Modal(modal);
  },

  /**
   * ABRIR MODAL
   */
  abrirModal: function(id) {
    const modalElement = document.getElementById(id);
    if (modalElement) {
      const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
      modal.show();
    }
  },

  /**
   * CERRAR MODAL
   */
  cerrarModal: function(id) {
    const modalElement = document.getElementById(id);
    if (modalElement) {
      const modal = bootstrap.Modal.getInstance(modalElement);
      if (modal) {
        modal.hide();
      }
    }
  },

  /**
   * MODAL DE CONFIRMACIÓN
   */
  confirmar: function(titulo, mensaje, callbackOk, callbackCancel = null) {
    return this.crearModal(
      'modal-confirmacion-' + Date.now(),
      titulo,
      `<p>${mensaje}</p>`,
      [
        {
          texto: 'Confirmar',
          tipo: 'primary',
          atributos: `onclick="this.closest('.modal').querySelector('[data-confirm-ok]').click()"`
        }
      ]
    );
  },

  /**
   * MODAL DE ALERTA
   */
  alerta: function(titulo, mensaje, tipo = 'info') {
    const tiposClase = {
      'error': 'alert-danger',
      'success': 'alert-success',
      'warning': 'alert-warning',
      'info': 'alert-info'
    };

    const contenido = `
      <div class="alert ${tiposClase[tipo] || 'alert-info'}" role="alert">
        ${mensaje}
      </div>
    `;

    return this.crearModal('modal-alerta-' + Date.now(), titulo, contenido);
  },

  /**
   * MODAL DE CARGANDO
   */
  mostrarCargando: function() {
    const modal = this.crearModal(
      'modal-cargando',
      'Cargando',
      '<div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>'
    );
    modal.show();
    return modal;
  },

  /**
   * CERRAR MODAL DE CARGANDO
   */
  cerrarCargando: function() {
    this.cerrarModal('modal-cargando');
  },

  /**
   * MODAL CON FORMULARIO
   */
  formulario: function(titulo, campos, callbackEnvio) {
    const formId = 'formulario-' + Date.now();
    let html = `<form id="${formId}" class="needs-validation" novalidate>`;

    campos.forEach(campo => {
      html += `
        <div class="mb-3">
          <label for="${campo.id}" class="form-label">${campo.label}</label>
          <input 
            type="${campo.tipo || 'text'}" 
            class="form-control" 
            id="${campo.id}"
            name="${campo.nombre || campo.id}"
            ${campo.requerido ? 'required' : ''}
            ${campo.atributos || ''}
          >
          <div class="invalid-feedback" id="${campo.id}-feedback"></div>
        </div>
      `;
    });

    html += `</form>`;

    return this.crearModal(formId + '-modal', titulo, html, [
      {
        texto: 'Enviar',
        tipo: 'primary',
        atributos: `onclick="Modales.enviarFormulario('${formId}')"`
      }
    ]);
  },

  /**
   * ENVIAR FORMULARIO
   */
  enviarFormulario: function(formId) {
    const form = document.getElementById(formId);
    if (form && form.checkValidity() === false) {
      form.classList.add('was-validated');
      return;
    }

    const datos = new FormData(form);
    const objeto = Object.fromEntries(datos);
    console.log('Formulario enviado:', objeto);
    // Aquí iría la lógica de envío
  },

  /**
   * MODAL CON CONTENIDO PERSONALIZADO
   */
  personalizado: function(id, titulo, contenido, tamano = 'modal-lg') {
    const modal = document.createElement('div');
    modal.id = id;
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');
    modal.innerHTML = `
      <div class="modal-dialog ${tamano}">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">${titulo}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            ${contenido}
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    return new bootstrap.Modal(modal);
  },

  /**
   * DESTRUIR MODAL
   */
  destruir: function(id) {
    const modalElement = document.getElementById(id);
    if (modalElement) {
      const modal = bootstrap.Modal.getInstance(modalElement);
      if (modal) {
        modal.dispose();
      }
      modalElement.remove();
    }
  },

  /**
   * ESCUCHAR EVENTOS DEL MODAL
   */
  enEvento: function(id, evento, callback) {
    const modalElement = document.getElementById(id);
    if (modalElement) {
      modalElement.addEventListener(evento, callback);
    }
  },
};

// EXPORT para CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Modales;
}
window.Modales = Modales;

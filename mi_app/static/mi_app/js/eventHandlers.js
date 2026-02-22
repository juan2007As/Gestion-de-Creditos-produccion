/**
 * EVENTHANDLERS.JS
 * ============================================================================
 * Propósito: Manejadores de eventos globales y delegación de eventos
 * ============================================================================
 */

const EventHandlers = {
  /**
   * INICIALIZAR LISTENERS GLOBALES
   */
  inicializar: function() {
    this.delegarEventos();
    this.escucharResize();
    this.escucharScroll();
    this.escucharKeyboard();
    Utils.log('EventHandlers inicializado', 'info');
  },

  /**
   * DELEGACIÓN DE EVENTOS
   */
  delegarEventos: function() {
    // Click en botones de acción
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-accion]')) {
        const accion = e.target.getAttribute('data-accion');
        this.manejarAccion(accion, e.target);
      }
    });

    // Submit de formularios
    document.addEventListener('submit', (e) => {
      if (e.target.matches('[data-ajax-submit]')) {
        e.preventDefault();
        const url = e.target.getAttribute('data-ajax-submit');
        Formularios.enviarAjax(e.target.id, url);
      }
    });

    // Validación en tiempo real
    document.addEventListener('change', (e) => {
      if (e.target.matches('[data-validar]')) {
        const regla = e.target.getAttribute('data-validar');
        const validacion = Formularios.validarCampo(e.target, e.target.value, regla);
        if (!validacion.valido) {
          Formularios.mostrarError(e.target, validacion.error);
        } else {
          Formularios.limpiarError(e.target);
        }
      }
    });
  },

  /**
   * ESCUCHAR RESIZE
   */
  escucharResize: function() {
    window.addEventListener('resize', Utils.debounce(() => {
      const viewport = Utils.getViewport();
      Utils.log(`Window resized: ${viewport.width}x${viewport.height}`, 'debug');
      this.actualizarResponsivo();
    }, 250));
  },

  /**
   * ESCUCHAR SCROLL
   */
  escucharScroll: function() {
    window.addEventListener('scroll', Utils.throttle(() => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight;
      const winHeight = window.innerHeight;
      const scrollPercent = (scrollTop + winHeight) / docHeight;

      // Detectar cuando se llega al final
      if (scrollPercent > 0.9) {
        Utils.log('Cerca del final de la página', 'debug');
        document.body.classList.add('near-bottom');
      } else {
        document.body.classList.remove('near-bottom');
      }

      // Botón "Ir arriba"
      if (scrollTop > 300) {
        document.body.classList.add('scroll-active');
      } else {
        document.body.classList.remove('scroll-active');
      }
    }, 300));
  },

  /**
   * ESCUCHAR KEYBOARD
   */
  escucharKeyboard: function() {
    document.addEventListener('keydown', (e) => {
      // ESC para cerrar modal
      if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
          const m = bootstrap.Modal.getInstance(modal);
          if (m) m.hide();
        });
      }

      // Ctrl+S para guardar
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        Utils.log('Guardando...', 'info');
        // Trigger guardar
      }

      // Ctrl+Shift+D para debug
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'd') {
        e.preventDefault();
        CONFIG.DEBUG = !CONFIG.DEBUG;
        Utils.log(`Debug mode: ${CONFIG.DEBUG}`, 'info');
      }
    });
  },

  /**
   * MANEJAR ACCIONES DELEGADAS
   */
  manejarAccion: function(accion, elemento) {
    Utils.log(`Acción: ${accion}`, 'debug');

    const acciones = {
      'eliminar': () => this.confirmarEliminar(elemento),
      'editar': () => this.abrirEditar(elemento),
      'ver': () => this.verDetalles(elemento),
      'descargar': () => this.descargar(elemento),
      'exportar': () => this.exportar(elemento),
      'imprimir': () => this.imprimir(elemento),
      'volver': () => window.history.back(),
      'recargar': () => window.location.reload(),
    };

    if (acciones[accion]) {
      acciones[accion]();
    }
  },

  /**
   * CONFIRMAR ELIMINACIÓN
   */
  confirmarEliminar: function(elemento) {
    const id = elemento.getAttribute('data-id');
    if (!confirm('¿Confirma que desea eliminar este elemento?')) return;

    const url = elemento.getAttribute('data-url');
    Ajax.delete(url, (data) => {
      Modales.alerta('Éxito', 'Elemento eliminado correctamente', 'success').show();
      setTimeout(() => window.location.reload(), 2000);
    });
  },

  /**
   * ABRIR FORMULARIO DE EDICIÓN
   */
  abrirEditar: function(elemento) {
    const id = elemento.getAttribute('data-id');
    const url = elemento.getAttribute('data-url');
    Utils.log(`Editando ${id}`, 'debug');
    // Implementar lógica de edición
  },

  /**
   * VER DETALLES
   */
  verDetalles: function(elemento) {
    const id = elemento.getAttribute('data-id');
    const url = elemento.getAttribute('data-url');
    Utils.log(`Ver detalles de ${id}`, 'debug');
    // Implementar lógica de ver detalles
  },

  /**
   * DESCARGAR
   */
  descargar: function(elemento) {
    const url = elemento.getAttribute('data-url');
    Ajax.descargarArchivo(url, 'archivo');
  },

  /**
   * EXPORTAR
   */
  exportar: function(elemento) {
    const formato = elemento.getAttribute('data-formato') || 'csv';
    Utils.log(`Exportando en ${formato}`, 'debug');
    // Implementar exportación
  },

  /**
   * IMPRIMIR
   */
  imprimir: function(elemento) {
    const idElemento = elemento.getAttribute('data-id');
    const elemento_print = document.getElementById(idElemento);
    if (elemento_print) {
      const contenido = elemento_print.innerHTML;
      const ventana = window.open('', '', 'height=400,width=800');
      ventana.document.write(contenido);
      ventana.document.close();
      ventana.print();
    }
  },

  /**
   * ACTUALIZAR RESPONSIVE
   */
  actualizarResponsivo: function() {
    const viewport = Utils.getViewport();
    if (Utils.isMobile()) {
      document.body.classList.remove('tablet', 'desktop');
      document.body.classList.add('mobile');
    } else if (Utils.isTablet()) {
      document.body.classList.remove('mobile', 'desktop');
      document.body.classList.add('tablet');
    } else {
      document.body.classList.remove('mobile', 'tablet');
      document.body.classList.add('desktop');
    }
  },

  /**
   * NOTIFICACIÓN
   */
  mostrarNotificacion: function(titulo, mensaje, tipo = 'info') {
    const notificacion = document.createElement('div');
    notificacion.className = `alert alert-${tipo} alert-dismissible fade show`;
    notificacion.innerHTML = `
      <strong>${titulo}:</strong> ${mensaje}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const contenedor = document.querySelector('.notifications-container') || document.body;
    contenedor.appendChild(notificacion);

    setTimeout(() => {
      notificacion.remove();
    }, CONFIG.TIMEOUT_NOTIFICATION);
  },

  /**
   * LOADING GLOBAL
   */
  mostrarCargando: function(mostrar = true) {
    let loader = document.getElementById('global-loader');
    if (!loader) {
      loader = document.createElement('div');
      loader.id = 'global-loader';
      loader.className = 'global-loader';
      loader.innerHTML = '<div class="spinner-border"></div>';
      document.body.appendChild(loader);
    }
    loader.style.display = mostrar ? 'flex' : 'none';
  },

  /**
   * DARK MODE TOGGLE
   * Cambia entre tema claro y oscuro y SINCRONIZA INMEDIATAMENTE
   */
  toggleDarkMode: function() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    const nuevoTema = isDark ? 'light' : 'dark';
    
    // Suppress transiciones durante cambio de tema
    html.style.transition = 'none';
    
    // 1. Actualizar HTML tag INMEDIATAMENTE
    html.setAttribute('data-theme', nuevoTema);
    
    // Re-enable transiciones
    setTimeout(() => {
      html.style.transition = '';
    }, 50);
    
    // 2. Guardar en localStorage
    Utils.setLocalStorage('theme', nuevoTema);
    
    // 3. Disparar evento personalizado para que otros scripts sepan del cambio
    const evento = new CustomEvent('themeChanged', { 
      detail: { tema: nuevoTema }
    });
    document.dispatchEvent(evento);
  },

  /**
   * CARGAR TEMA GUARDADO
   * Se ejecuta al cargar la página para restaurar el tema
   */
  cargarTemaGuardado: function() {
    const tema = Utils.getLocalStorage('theme') || 'light';
    document.documentElement.setAttribute('data-theme', tema);
  },

  /**
   * INICIAR SINCRONIZACIÓN DE TEMA (BUG FIX #3 - ELIMINADO POLLING)
   * Sincroniza el tema del localStorage sin flickering
   * 
   * Método: 
   * - Usa storage event solamente (sin polling)
   * - Escucha cambios desde otras tabs
   * - Previene flickering causado por polling continuo
   */
  iniciarSincronizacionTema: function() {
    // Sincronizar cuando hay cambios de visibilidad (tab activo/inactivo)
    document.addEventListener('visibilitychange', () => {
      const temaLocal = Utils.getLocalStorage('theme') || 'light';
      document.documentElement.setAttribute('data-theme', temaLocal);
    });
    
    // Sincronizar cuando hay cambios en localStorage desde otras tabs
    window.addEventListener('storage', (e) => {
      if (e.key === 'theme') {
        const temaLocal = Utils.getLocalStorage('theme') || 'light';
        document.documentElement.setAttribute('data-theme', temaLocal);
      }
    });
  },
};

// Inicializar cuando DOM está listo
document.addEventListener('DOMContentLoaded', () => {
  EventHandlers.inicializar();
  EventHandlers.cargarTemaGuardado();
  EventHandlers.iniciarSincronizacionTema();  // ← BUG FIX #3: Sincronizar tema continuamente
});

// EXPORT para CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = EventHandlers;
}

/**
 * MAIN.JS
 * ============================================================================
 * Propósito: Punto de entrada principal de la aplicación
 * ============================================================================
 */

console.log('=== PROYECTO JOHN - APLICACIÓN INICIADA ===');

// Verificar que todos los módulos estén cargados
const modulosRequeridos = [
  'CONFIG',
  'Utils',
  'Validadores',
  'Modales',
  'Dropdowns',
  'Formularios',
  'Ajax',
  'EventHandlers'
];

// Reintentos para módulos que pueden estar cargándose
let verificarModulosIntentos = 0;
const MAX_REINTENTOS = 5;

function verificarModulos(retryCount = 0) {
  const modulosFaltantes = modulosRequeridos.filter(modulo => {
    if (typeof window[modulo] === 'undefined') {
      console.warn(`⏳ Módulo pendiente: ${modulo}`);
      return true;
    }
    console.log(`✅ Módulo cargado: ${modulo}`);
    return false;
  });

  if (modulosFaltantes.length > 0) {
    if (retryCount < MAX_REINTENTOS) {
      console.warn(`⏳ Falta(n) ${modulosFaltantes.length} módulo(s): ${modulosFaltantes.join(', ')} (reintento ${retryCount + 1}/${MAX_REINTENTOS})`);
      return false;
    } else {
      console.warn(`⚠️  Advertencia: ${modulosFaltantes.length} módulo(s) aún no disponibles después de ${MAX_REINTENTOS} reintentos. Continuando...`);
      return true; // Continuar de todos modos
    }
  }

  console.log('\n✅ Todos los módulos cargados correctamente');
  return true;
}

// APP PRINCIPAL
const App = {
  /**
   * INICIALIZAR APLICACIÓN
   */
  init: function(retryCount = 0) {
    console.log('\n🚀 Inicializando aplicación...');

    if (!verificarModulos(retryCount)) {
      // Reintentar en 100ms
      if (retryCount < MAX_REINTENTOS) {
        console.log(`⏳ Reintentando cargar módulos (${retryCount + 1}/${MAX_REINTENTOS})...`);
        setTimeout(() => {
          this.init(retryCount + 1);
        }, 100);
        return;
      } else {
        console.warn('⚠️  Algunos módulos aún no están disponibles, pero continuando de todas formas...');
      }
    }

    // Inicializar componentes
    this.inicializarBootstrap();
    this.configurarGlobales();
    this.cargarConfiguracion();
    this.setupErrorHandler();

    console.log('✅ Aplicación inicializada exitosamente\n');

    // Ejecutar callback de inicialización si existe
    if (typeof onAppReady === 'function') {
      onAppReady();
    }
  },

  /**
   * INICIALIZAR BOOTSTRAP
   */
  inicializarBootstrap: function() {
    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl);
    });

    console.log('✅ Bootstrap inicializado');
  },

  /**
   * CONFIGURAR GLOBALES
   */
  configurarGlobales: function() {
    // Exponer módulos globales (con fallbacks defensivos)
    window.app = this;
    window.utils = typeof Utils !== 'undefined' ? Utils : {};
    window.validadores = typeof Validadores !== 'undefined' ? Validadores : {};
    window.modales = typeof Modales !== 'undefined' ? Modales : {};
    window.dropdowns = typeof Dropdowns !== 'undefined' ? Dropdowns : {};
    window.formularios = typeof Formularios !== 'undefined' ? Formularios : {};
    window.ajax = typeof Ajax !== 'undefined' ? Ajax : {};
    window.config = typeof CONFIG !== 'undefined' ? CONFIG : {};

    console.log('✅ Globales configurados');
  },

  /**
   * CARGAR CONFIGURACIÓN
   */
  cargarConfiguracion: function() {
    // Cargar tema guardado
    const tema = Utils.getLocalStorage('theme') || 'light';
    document.documentElement.setAttribute('data-theme', tema);

    // Cargar preferencias del usuario
    const preferencias = Utils.getLocalStorage('preferencias') || {};

    // Aplicar configuración
    if (CONFIG.DEBUG) {
      console.log('🔧 DEBUG MODE ACTIVO');
      console.log('CONFIG:', CONFIG);
    }

    console.log('✅ Configuración cargada');
  },

  /**
   * SETUP ERROR HANDLER
   */
  setupErrorHandler: function() {
    window.addEventListener('error', (event) => {
      Utils.log(`Error: ${event.message} en ${event.filename}:${event.lineno}`, 'error');
      console.error(event.error);
    });

    window.addEventListener('unhandledrejection', (event) => {
      Utils.log(`Promise rechazada: ${event.reason}`, 'error');
      console.error(event.reason);
    });

    console.log('✅ Error handler configurado');
  },

  /**
   * OBTENER INFORMACIÓN DE LA APLICACIÓN
   */
  getInfo: function() {
    return {
      nombre: 'Gestión Préstamos',
      versión: '1.0.0',
      ambiente: CONFIG.DEBUG ? 'desarrollo' : 'producción',
      módulos: modulosRequeridos.length,
      breakpoints: CONFIG.BREAKPOINTS,
    };
  },

  /**
   * REINICIAR APLICACIÓN
   */
  reiniciar: function() {
    console.log('🔄 Reiniciando aplicación...');
    window.location.reload();
  },

  /**
   * DESTRUIR APLICACIÓN (Cleanup)
   */
  destruir: function() {
    console.log('💥 Destruyendo aplicación...');
    // Limpiar event listeners
    document.removeEventListener('DOMContentLoaded', this.init);
    // Limpiar datos del localStorage si es necesario
    console.log('✅ Aplicación destruida');
  },
};

// Auto-inicializar cuando DOM está listo
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});

// Exponer APP globalmente
window.App = App;

// Para desarrollo - mostrar info en consola
if (CONFIG.DEBUG) {
  console.log('%c📊 APP INFO', 'color: #007bff; font-size: 14px; font-weight: bold;');
  console.table(App.getInfo());
  console.log('%c🔗 Acceso desde consola', 'color: #28a745; font-size: 12px; font-weight: bold;');
  console.log('- app.getInfo()');
  console.log('- app.reiniciar()');
  console.log('- CONFIG, Utils, Validadores, etc...');
}

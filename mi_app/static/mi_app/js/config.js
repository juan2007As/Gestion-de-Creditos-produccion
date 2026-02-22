/**
 * CONFIG.JS
 * ============================================================================
 * Propósito: Configuración global, constantes y variables de entorno
 * ============================================================================
 */

const CONFIG = {
  // URLs Y ENDPOINTS
  API_BASE_URL: '/api/',
  ENDPOINTS: {
    CLIENTES: '/api/clientes/',
    PRESTAMOS: '/api/prestamos/',
    CUOTAS: '/api/cuotas/',
    PAGOS: '/api/pagos/',
    REPORTES: '/api/reportes/',
    BUSQUEDA: '/buscar/',
  },

  // TIMEOUTS Y DELAYS
  TIMEOUT_AJAX: 30000,
  TIMEOUT_MODAL: 300,
  TIMEOUT_NOTIFICATION: 5000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,

  // PAGINACIÓN
  ITEMS_PER_PAGE: 10,
  MAX_ITEMS_DISPLAY: 100,

  // VALIDACIÓN
  VALIDATION: {
    MIN_LENGTH_CEDULA: 8,
    MAX_LENGTH_CEDULA: 12,
    MIN_LENGTH_PASSWORD: 6,
    MAX_LENGTH_PASSWORD: 128,
  },

  // FORMATOS
  DATE_FORMAT: 'YYYY-MM-DD',
  TIME_FORMAT: 'HH:mm:ss',
  CURRENCY_FORMAT: 'USD',

  // DEBUG MODE
  DEBUG: true,
  LOG_LEVEL: 'debug', // 'debug', 'info', 'warn', 'error'

  // FEATURES
  FEATURES: {
    DARK_MODE: true,
    NOTIFICATIONS: true,
    ANALYTICS: false,
  },

  // COLORES Y TEMAS
  COLORS: {
    PRIMARY: '#007bff',
    SUCCESS: '#28a745',
    DANGER: '#dc3545',
    WARNING: '#ffc107',
    INFO: '#17a2b8',
  },

  // BREAKPOINTS RESPONSIVE
  BREAKPOINTS: {
    XS: 0,
    SM: 425,
    MD: 768,
    LG: 1024,
    XL: 1440,
    XXL: 2444,
  },
};

// EXPORT para CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}

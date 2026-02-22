/**
 * UTILS.JS
 * ============================================================================
 * Propósito: Funciones utilitarias genéricas y helpers globales
 * ============================================================================
 */

const Utils = {
  /**
   * LOG: Sistema de logging centralizado
   */
  log: function(message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
    
    switch(level) {
      case 'debug':
        if (CONFIG.LOG_LEVEL === 'debug') console.log(`${prefix} ${message}`);
        break;
      case 'info':
        console.info(`${prefix} ${message}`);
        break;
      case 'warn':
        console.warn(`${prefix} ${message}`);
        break;
      case 'error':
        console.error(`${prefix} ${message}`);
        break;
    }
  },

  /**
   * FORMATTERS
   */
  formatCurrency: function(value) {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP'
    }).format(value);
  },

  formatDate: function(date) {
    return new Date(date).toLocaleDateString('es-CO');
  },

  formatDateTime: function(dateTime) {
    return new Date(dateTime).toLocaleString('es-CO');
  },

  /**
   * PARSERS
   */
  parseJSON: function(str) {
    try {
      return JSON.parse(str);
    } catch (e) {
      this.log(`Error parsing JSON: ${e.message}`, 'error');
      return null;
    }
  },

  stringifyJSON: function(obj) {
    try {
      return JSON.stringify(obj);
    } catch (e) {
      this.log(`Error stringifying JSON: ${e.message}`, 'error');
      return null;
    }
  },

  /**
   * DOM MANIPULATION
   */
  getElementById: function(id) {
    return document.getElementById(id);
  },

  querySelector: function(selector) {
    return document.querySelector(selector);
  },

  querySelectorAll: function(selector) {
    return document.querySelectorAll(selector);
  },

  addClass: function(element, className) {
    if (element) element.classList.add(className);
  },

  removeClass: function(element, className) {
    if (element) element.classList.remove(className);
  },

  toggleClass: function(element, className) {
    if (element) element.classList.toggle(className);
  },

  hasClass: function(element, className) {
    return element ? element.classList.contains(className) : false;
  },

  /**
   * STORAGE
   */
  setLocalStorage: function(key, value) {
    try {
      localStorage.setItem(key, this.stringifyJSON(value));
    } catch (e) {
      this.log(`Error setting localStorage: ${e.message}`, 'error');
    }
  },

  getLocalStorage: function(key) {
    try {
      const value = localStorage.getItem(key);
      return value ? this.parseJSON(value) : null;
    } catch (e) {
      this.log(`Error getting localStorage: ${e.message}`, 'error');
      return null;
    }
  },

  removeLocalStorage: function(key) {
    try {
      localStorage.removeItem(key);
    } catch (e) {
      this.log(`Error removing from localStorage: ${e.message}`, 'error');
    }
  },

  /**
   * ARRAYS
   */
  unique: function(array) {
    return [...new Set(array)];
  },

  sortBy: function(array, key) {
    return array.sort((a, b) => a[key] > b[key] ? 1 : -1);
  },

  groupBy: function(array, key) {
    return array.reduce((result, item) => {
      const group = item[key];
      result[group] = result[group] || [];
      result[group].push(item);
      return result;
    }, {});
  },

  /**
   * STRINGS
   */
  capitalize: function(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  },

  trim: function(str) {
    return str.trim();
  },

  slugify: function(str) {
    return str.toLowerCase().replace(/[^\w ]+/g, '').replace(/ +/g, '-');
  },

  /**
   * VALIDATORS
   */
  isEmpty: function(value) {
    return value === null || value === undefined || value === '';
  },

  isEmail: function(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  },

  isPhoneNumber: function(phone) {
    return /^\d{7,15}$/.test(phone.replace(/\D/g, ''));
  },

  /**
   * TIME UTILITIES
   */
  delay: function(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  },

  debounce: function(func, wait) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  },

  throttle: function(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  /**
   * DEVICE DETECTION
   */
  isMobile: function() {
    return window.innerWidth < CONFIG.BREAKPOINTS.MD;
  },

  isTablet: function() {
    return window.innerWidth >= CONFIG.BREAKPOINTS.MD && window.innerWidth < CONFIG.BREAKPOINTS.LG;
  },

  isDesktop: function() {
    return window.innerWidth >= CONFIG.BREAKPOINTS.LG;
  },

  getViewport: function() {
    return {
      width: window.innerWidth,
      height: window.innerHeight,
    };
  },
};

// EXPORT para CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Utils;
}

/**
 * VALIDADORES.JS
 * ============================================================================
 * Propósito: Funciones de validación reutilizables para formularios y datos
 * ============================================================================
 */

const Validadores = {
  /**
   * CEDULA
   */
  validarCedula: function(cedula) {
    cedula = cedula.toString().trim();
    
    // Validar rango
    if (cedula.length < CONFIG.VALIDATION.MIN_LENGTH_CEDULA || 
        cedula.length > CONFIG.VALIDATION.MAX_LENGTH_CEDULA) {
      return { valid: false, error: 'Cédula debe tener entre 8 y 12 caracteres' };
    }

    // Validar que sea numérica
    if (!/^\d+$/.test(cedula)) {
      return { valid: false, error: 'Cédula debe contener solo números' };
    }

    return { valid: true, error: null };
  },

  /**
   * EMAIL
   */
  validarEmail: function(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!regex.test(email)) {
      return { valid: false, error: 'Formato de email inválido' };
    }
    return { valid: true, error: null };
  },

  /**
   * TELÉFONO
   */
  validarTelefono: function(telefono) {
    const cleaned = telefono.replace(/\D/g, '');
    if (cleaned.length < 7 || cleaned.length > 15) {
      return { valid: false, error: 'Teléfono debe tener entre 7 y 15 dígitos' };
    }
    return { valid: true, error: null };
  },

  /**
   * CONTRASEÑA
   */
  validarPassword: function(password) {
    if (password.length < CONFIG.VALIDATION.MIN_LENGTH_PASSWORD) {
      return { 
        valid: false, 
        error: `Contraseña debe tener mínimo ${CONFIG.VALIDATION.MIN_LENGTH_PASSWORD} caracteres` 
      };
    }

    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

    if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
      return {
        valid: false,
        error: 'Contraseña debe incluir mayúsculas, minúsculas y números'
      };
    }

    return { valid: true, error: null };
  },

  /**
   * FECHA
   */
  validarFecha: function(fecha) {
    const date = new Date(fecha);
    if (isNaN(date.getTime())) {
      return { valid: false, error: 'Formato de fecha inválido' };
    }

    if (date > new Date()) {
      return { valid: false, error: 'La fecha no puede ser en el futuro' };
    }

    return { valid: true, error: null };
  },

  /**
   * MONTO MONETARIO
   */
  validarMonto: function(monto, minimo = 0, maximo = null) {
    const numMonto = parseFloat(monto);

    if (isNaN(numMonto)) {
      return { valid: false, error: 'Monto debe ser un número' };
    }

    if (numMonto < minimo) {
      return { valid: false, error: `Monto mínimo es ${minimo}` };
    }

    if (maximo !== null && numMonto > maximo) {
      return { valid: false, error: `Monto máximo es ${maximo}` };
    }

    return { valid: true, error: null };
  },

  /**
   * NÚMERO
   */
  validarNumero: function(numero, entero = false) {
    const num = parseFloat(numero);

    if (isNaN(num)) {
      return { valid: false, error: 'Debe ser un número válido' };
    }

    if (entero && !Number.isInteger(num)) {
      return { valid: false, error: 'Debe ser un número entero' };
    }

    return { valid: true, error: null };
  },

  /**
   * TEXTO
   */
  validarTexto: function(texto, minLength = 1, maxLength = null) {
    if (!texto || texto.trim().length < minLength) {
      return { valid: false, error: `Texto debe tener mínimo ${minLength} caracteres` };
    }

    if (maxLength && texto.length > maxLength) {
      return { valid: false, error: `Texto no puede exceder ${maxLength} caracteres` };
    }

    return { valid: true, error: null };
  },

  /**
   * CAMPO REQUERIDO
   */
  validarRequerido: function(value) {
    if (!value || (typeof value === 'string' && !value.trim())) {
      return { valid: false, error: 'Este campo es requerido' };
    }
    return { valid: true, error: null };
  },

  /**
   * VALIDAR FORMULARIO COMPLETO
   */
  validarFormulario: function(datos, reglas) {
    const errores = {};
    let esValido = true;

    for (const campo in reglas) {
      const regla = reglas[campo];
      const valor = datos[campo];
      const validacion = regla(valor);

      if (!validacion.valid) {
        errores[campo] = validacion.error;
        esValido = false;
      }
    }

    return { valid: esValido, errores };
  },

  /**
   * COMPARAR DOS VALORES
   */
  validarCoincidencia: function(valor1, valor2) {
    if (valor1 !== valor2) {
      return { valid: false, error: 'Los valores no coinciden' };
    }
    return { valid: true, error: null };
  },

  /**
   * VALIDAR URL
   */
  validarURL: function(url) {
    try {
      new URL(url);
      return { valid: true, error: null };
    } catch {
      return { valid: false, error: 'URL inválida' };
    }
  },

  /**
   * VALIDAR JSON
   */
  validarJSON: function(str) {
    try {
      JSON.parse(str);
      return { valid: true, error: null };
    } catch {
      return { valid: false, error: 'JSON inválido' };
    }
  },
};

// EXPORT para CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Validadores;
}

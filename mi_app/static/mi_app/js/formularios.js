/**
 * FORMULARIOS.JS
 * ============================================================================
 * Propósito: Gestionar formularios, validación en cliente y envío
 * ============================================================================
 */

const Formularios = {
  /**
   * VALIDAR FORMULARIO
   */
  validar: function(idFormulario) {
    const form = document.getElementById(idFormulario);
    if (!form) return false;

    let esValido = true;
    const campos = form.querySelectorAll('[data-validar]');

    campos.forEach(campo => {
      const regla = campo.getAttribute('data-validar');
      const valor = campo.value;
      const validacion = this.validarCampo(campo, valor, regla);

      if (!validacion.valido) {
        this.mostrarError(campo, validacion.error);
        esValido = false;
      } else {
        this.limpiarError(campo);
      }
    });

    return esValido;
  },

  /**
   * VALIDAR CAMPO INDIVIDUAL
   */
  validarCampo: function(campo, valor, regla) {
    if (regla === 'requerido' && !valor) {
      return { valido: false, error: 'Este campo es requerido' };
    }

    if (regla === 'email' && valor && !Utils.isEmail(valor)) {
      return { valido: false, error: 'Email inválido' };
    }

    if (regla === 'telefono' && valor) {
      const result = Validadores.validarTelefono(valor);
      if (!result.valid) return { valido: false, error: result.error };
    }

    if (regla === 'cedula' && valor) {
      const result = Validadores.validarCedula(valor);
      if (!result.valid) return { valido: false, error: result.error };
    }

    if (regla === 'minimo') {
      const minimo = campo.getAttribute('data-minimo') || 0;
      if (valor.length < minimo) {
        return { valido: false, error: `Mínimo ${minimo} caracteres` };
      }
    }

    if (regla === 'maximo') {
      const maximo = campo.getAttribute('data-maximo') || 100;
      if (valor.length > maximo) {
        return { valido: false, error: `Máximo ${maximo} caracteres` };
      }
    }

    return { valido: true, error: null };
  },

  /**
   * MOSTRAR ERROR EN CAMPO
   */
  mostrarError: function(campo, error) {
    Utils.addClass(campo, 'is-invalid');
    
    let feedback = campo.nextElementSibling;
    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
      feedback = document.createElement('div');
      feedback.className = 'invalid-feedback';
      campo.parentNode.insertBefore(feedback, campo.nextSibling);
    }
    feedback.textContent = error;
  },

  /**
   * LIMPIAR ERROR DE CAMPO
   */
  limpiarError: function(campo) {
    Utils.removeClass(campo, 'is-invalid');
    const feedback = campo.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
      feedback.textContent = '';
    }
  },

  /**
   * OBTENER DATOS DEL FORMULARIO
   */
  obtenerDatos: function(idFormulario) {
    const form = document.getElementById(idFormulario);
    if (!form) return null;

    const formData = new FormData(form);
    const datos = {};

    formData.forEach((valor, clave) => {
      if (datos[clave]) {
        // Si ya existe, convertir a array
        if (!Array.isArray(datos[clave])) {
          datos[clave] = [datos[clave]];
        }
        datos[clave].push(valor);
      } else {
        datos[clave] = valor;
      }
    });

    return datos;
  },

  /**
   * ESTABLECER DATOS EN FORMULARIO
   */
  establecerDatos: function(idFormulario, datos) {
    const form = document.getElementById(idFormulario);
    if (!form) return;

    for (const clave in datos) {
      const campo = form.querySelector(`[name="${clave}"]`);
      if (campo) {
        if (campo.type === 'checkbox' || campo.type === 'radio') {
          campo.checked = datos[clave];
        } else {
          campo.value = datos[clave];
        }
      }
    }
  },

  /**
   * LIMPIAR FORMULARIO
   */
  limpiar: function(idFormulario) {
    const form = document.getElementById(idFormulario);
    if (form) {
      form.reset();
      form.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
      form.querySelectorAll('.is-invalid').forEach(el => Utils.removeClass(el, 'is-invalid'));
    }
  },

  /**
   * DESHABILITAR FORMULARIO
   */
  deshabilitar: function(idFormulario, deshabilitado = true) {
    const form = document.getElementById(idFormulario);
    if (!form) return;

    const campos = form.querySelectorAll('input, select, textarea, button');
    campos.forEach(campo => {
      campo.disabled = deshabilitado;
    });
  },

  /**
   * ENVIAR FORMULARIO VIA AJAX
   */
  enviarAjax: function(idFormulario, url, metodo = 'POST', callback = null) {
    if (!this.validar(idFormulario)) {
      Utils.log('Formulario no válido', 'warn');
      return;
    }

    const form = document.getElementById(idFormulario);
    const datos = new FormData(form);

    this.deshabilitar(idFormulario, true);

    fetch(url, {
      method: metodo,
      body: datos,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': this.obtenerCSRF(),
      }
    })
    .then(response => response.json())
    .then(data => {
      if (callback) callback(data);
      Utils.log('Envío exitoso', 'info');
    })
    .catch(error => {
      Utils.log(`Error: ${error.message}`, 'error');
    })
    .finally(() => {
      this.deshabilitar(idFormulario, false);
    });
  },

  /**
   * OBTENER TOKEN CSRF
   */
  obtenerCSRF: function() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
  },

  /**
   * AGREGAR VALIDACIÓN EN TIEMPO REAL
   */
  agregarValidacionEnTiempoReal: function(idFormulario) {
    const form = document.getElementById(idFormulario);
    if (!form) return;

    const campos = form.querySelectorAll('[data-validar]');
    campos.forEach(campo => {
      campo.addEventListener('blur', () => {
        const regla = campo.getAttribute('data-validar');
        const validacion = this.validarCampo(campo, campo.value, regla);

        if (!validacion.valido) {
          this.mostrarError(campo, validacion.error);
        } else {
          this.limpiarError(campo);
        }
      });
    });
  },

  /**
   * SERIALIZAR FORMULARIO
   */
  serializar: function(idFormulario) {
    const form = document.getElementById(idFormulario);
    if (!form) return '';

    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    return params.toString();
  },

  /**
   * CONTAR CARACTERES EN CAMPO
   */
  agregarContador: function(idCampo, idContador, maximo = null) {
    const campo = document.getElementById(idCampo);
    const contador = document.getElementById(idContador);

    if (!campo || !contador) return;

    const actualizar = () => {
      const cantidad = campo.value.length;
      if (maximo) {
        contador.textContent = `${cantidad}/${maximo}`;
      } else {
        contador.textContent = cantidad;
      }
    };

    campo.addEventListener('input', actualizar);
    actualizar();
  },

  /**
   * MOSTRAR LOADER EN BOTÓN
   */
  mostrarLoaderBoton: function(idBoton) {
    const boton = document.getElementById(idBoton);
    if (!boton) return;

    const texto = boton.textContent;
    boton.disabled = true;
    boton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Cargando...';
    return texto;
  },

  /**
   * OCULTAR LOADER EN BOTÓN
   */
  ocultarLoaderBoton: function(idBoton, textoOriginal) {
    const boton = document.getElementById(idBoton);
    if (!boton) return;

    boton.disabled = false;
    boton.textContent = textoOriginal;
  },
};

// EXPORT para CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Formularios;
}

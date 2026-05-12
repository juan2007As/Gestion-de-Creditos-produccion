/**
 * AJAX.JS
 * ============================================================================
 * Propósito: Funciones centralizadas para requests AJAX/Fetch
 * ============================================================================
 */

const Ajax = {
  /**
   * GET REQUEST
   */
  get: function(url, callback, errCallback = null) {
    fetch(url, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
      }
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (callback) callback(data);
    })
    .catch(error => {
      Utils.log(`GET Error: ${error.message}`, 'error');
      if (errCallback) errCallback(error);
    });
  },

  /**
   * POST REQUEST
   */
  post: function(url, datos, callback, errCallback = null) {
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': this.obtenerCSRF(),
      },
      body: JSON.stringify(datos)
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (callback) callback(data);
    })
    .catch(error => {
      Utils.log(`POST Error: ${error.message}`, 'error');
      if (errCallback) errCallback(error);
    });
  },

  /**
   * PUT REQUEST
   */
  put: function(url, datos, callback, errCallback = null) {
    fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': this.obtenerCSRF(),
      },
      body: JSON.stringify(datos)
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (callback) callback(data);
    })
    .catch(error => {
      Utils.log(`PUT Error: ${error.message}`, 'error');
      if (errCallback) errCallback(error);
    });
  },

  /**
   * DELETE REQUEST
   */
  delete: function(url, callback, errCallback = null) {
    fetch(url, {
      method: 'DELETE',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': this.obtenerCSRF(),
      }
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (callback) callback(data);
    })
    .catch(error => {
      Utils.log(`DELETE Error: ${error.message}`, 'error');
      if (errCallback) errCallback(error);
    });
  },

  /**
   * PATCH REQUEST
   */
  patch: function(url, datos, callback, errCallback = null) {
    fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': this.obtenerCSRF(),
      },
      body: JSON.stringify(datos)
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (callback) callback(data);
    })
    .catch(error => {
      Utils.log(`PATCH Error: ${error.message}`, 'error');
      if (errCallback) errCallback(error);
    });
  },

  /**
   * BUSQUEDA AJAX
   */
  buscar: function(url, termino, callback) {
    const params = new URLSearchParams({ q: termino });
    this.get(`${url}?${params}`, callback);
  },

  /**
   * CARGAR TABLA AJAX
   */
  cargarTabla: function(url, idTabla, callback = null) {
    this.get(url, (data) => {
      const tabla = document.getElementById(idTabla);
      if (!tabla) return;

      const tbody = tabla.querySelector('tbody');
      if (!tbody) return;

      tbody.innerHTML = '';

      if (data.resultados && data.resultados.length > 0) {
        data.resultados.forEach(row => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${row.id}</td>
            <td>${row.nombre || ''}</td>
            <td>${row.email || ''}</td>
            <td>
              <button class="btn btn-sm btn-primary">Editar</button>
              <button class="btn btn-sm btn-danger">Eliminar</button>
            </td>
          `;
          tbody.appendChild(tr);
        });
      } else {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Sin datos</td></tr>';
      }

      if (callback) callback(data);
    });
  },

  /**
   * CARGAR DATOS CON PAGINACIÓN
   */
  cargarPagina: function(url, pagina, callback) {
    const params = new URLSearchParams({ page: pagina });
    this.get(`${url}?${params}`, callback);
  },

  /**
   * UPLOAD DE ARCHIVO
   */
  subirArchivo: function(url, archivo, callback, errCallback = null) {
    const formData = new FormData();
    formData.append('archivo', archivo);

    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': this.obtenerCSRF(),
      },
      body: formData
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (callback) callback(data);
    })
    .catch(error => {
      Utils.log(`Upload Error: ${error.message}`, 'error');
      if (errCallback) errCallback(error);
    });
  },

  /**
   * REQUEST CON REINTENTOS
   */
  conReintentos: function(url, metodo = 'GET', datos = null, intentosRestantes = CONFIG.RETRY_ATTEMPTS) {
    return fetch(url, {
      method: metodo,
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': this.obtenerCSRF(),
      },
      body: datos ? JSON.stringify(datos) : null
    })
    .catch(error => {
      if (intentosRestantes > 0) {
        Utils.log(`Reintentando... (${intentosRestantes} intentos restantes)`, 'warn');
        return Utils.delay(CONFIG.RETRY_DELAY).then(() => 
          this.conReintentos(url, metodo, datos, intentosRestantes - 1)
        );
      }
      throw error;
    });
  },

  /**
   * OBTENER CSRF TOKEN
   */
  obtenerCSRF: function() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
  },

  /**
   * CANCELAR REQUEST (ABORT)
   */
  crearControlador: function() {
    return new AbortController();
  },

  /**
   * REQUEST CON TIMEOUT
   */
  conTimeout: function(url, metodo = 'GET', timeout = CONFIG.TIMEOUT_AJAX) {
    const controller = this.crearControlador();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    return fetch(url, {
      method: metodo,
      signal: controller.signal
    })
    .finally(() => clearTimeout(timeoutId));
  },

  /**
   * BATCH REQUEST (Múltiples requests)
   */
  batch: function(requests) {
    return Promise.all(requests.map(req => 
      fetch(req.url, {
        method: req.metodo || 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.obtenerCSRF(),
        },
        body: req.datos ? JSON.stringify(req.datos) : null
      }).then(r => r.json())
    ));
  },

  /**
   * DESCARGAR ARCHIVO
   */
  descargarArchivo: function(url, nombreArchivo) {
    const link = document.createElement('a');
    link.href = url;
    link.download = nombreArchivo || 'descarga';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
};

// EXPORT para CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Ajax;
}
window.Ajax = Ajax;

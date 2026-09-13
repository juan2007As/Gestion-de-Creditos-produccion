/**
 * ALTO #4: Real-time Mora Updates
 * Módulo para actualizar mora de cuotas en tiempo real
 * 
 * Características:
 * - Actualiza mora cada 30 segundos
 * - Muestra visual claro del aumento
 * - AJAX sin recargar página
 * - Compatible con mobile
 */

const MoraRealTime = (() => {
    // Configuración
    const config = {
        updateInterval: 30000,  // 30 segundos
        moraSelector: '.mora-realtime',
        timestampSelector: '.mora-timestamp',
        statusSelector: '.mora-status'
    };
    
    // Estado
    let updateTimers = {};
    let lastValues = {};
    
    /**
     * Obtiene mora actual de una cuota vía AJAX
     * @param {number} cuotaId - ID de la cuota
     * @returns {Promise} Promesa con datos de mora
     */
    async function fetchMoraActual(cuotaId) {
        try {
            const response = await fetch(`/api/cuota/${cuotaId}/mora-actual/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                console.warn(`Error fetching mora for cuota ${cuotaId}:`, response.status);
                return null;
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching mora:', error);
            return null;
        }
    }
    
    /**
     * Actualiza el elemento visual con la mora nueva
     * @param {number} cuotaId - ID de la cuota
     * @param {object} data - Datos de mora del servidor
     */
    function updateMoraDisplay(cuotaId, data) {
        if (!data || !data.success) return;
        
        // Selector único para esta cuota
        const moraElement = document.querySelector(
            `[data-cuota-id="${cuotaId}"] ${config.moraSelector}`
        );
        
        if (!moraElement) return;
        
        const moraValue = parseFloat(data.mora_diaria);
        const lastValue = lastValues[cuotaId] || 0;
        
        // Actualizar valor
        moraElement.textContent = `$${moraValue.toLocaleString('es-CO', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;
        
        // Animación si cambió (efecto de "actualización")
        if (moraValue !== lastValue) {
            moraElement.classList.add('mora-updated');
            setTimeout(() => {
                moraElement.classList.remove('mora-updated');
            }, 500);
        }
        
        // Actualizar timestamp
        const timestampElement = document.querySelector(
            `[data-cuota-id="${cuotaId}"] ${config.timestampSelector}`
        );
        
        if (timestampElement && data.timestamp) {
            const updateTime = new Date(data.timestamp);
            const timeAgo = getTimeAgo(updateTime);
            timestampElement.textContent = timeAgo;
        }
        
        // Actualizar estado visual
        const statusElement = document.querySelector(
            `[data-cuota-id="${cuotaId}"] ${config.statusSelector}`
        );
        
        if (statusElement) {
            statusElement.className = 'mora-status';
            statusElement.classList.add(`status-${data.estado.toLowerCase()}`);
            statusElement.textContent = data.estado;
        }
        
        // Guardar valor para verificar cambios
        lastValues[cuotaId] = moraValue;
    }
    
    /**
     * Calcula tiempo transcurrido en texto legible
     * @param {Date} date - Fecha
     * @returns {string} Texto del tiempo
     */
    function getTimeAgo(date) {
        const ahora = new Date();
        const diff = Math.floor((ahora - date) / 1000); // segundos
        
        if (diff < 60) return 'Hace unos segundos';
        const minutos = Math.floor(diff / 60);
        if (minutos < 60) return `Hace ${minutos} min`;
        const horas = Math.floor(minutos / 60);
        if (horas < 24) return `Hace ${horas}h`;
        const dias = Math.floor(horas / 24);
        return `Hace ${dias}d`;
    }
    
    /**
     * Inicia actualización automática para una cuota
     * @param {number} cuotaId - ID de la cuota
     */
    function iniciarActualizacion(cuotaId) {
        // Actualizar inmediatamente
        fetchMoraActual(cuotaId).then(data => {
            updateMoraDisplay(cuotaId, data);
        });
        
        // Actualizar periódicamente
        if (updateTimers[cuotaId]) {
            clearInterval(updateTimers[cuotaId]);
        }
        
        updateTimers[cuotaId] = setInterval(() => {
            fetchMoraActual(cuotaId).then(data => {
                updateMoraDisplay(cuotaId, data);
            });
        }, config.updateInterval);
    }
    
    /**
     * Detiene actualización automática para una cuota
     * @param {number} cuotaId - ID de la cuota
     */
    function detenerActualizacion(cuotaId) {
        if (updateTimers[cuotaId]) {
            clearInterval(updateTimers[cuotaId]);
            delete updateTimers[cuotaId];
        }
    }
    
    /**
     * Inicializa todos los elementos con mora en tiempo real
     */
    function init() {
        // Encontrar todos los elementos con data-cuota-id
        document.querySelectorAll('[data-cuota-id]').forEach(element => {
            const cuotaId = element.dataset.cuotaId;
            if (cuotaId) {
                iniciarActualizacion(parseInt(cuotaId));
            }
        });
    }
    
    /**
     * Limpia todos los timers cuando se descargan la página
     */
    function cleanup() {
        Object.keys(updateTimers).forEach(cuotaId => {
            detenerActualizacion(cuotaId);
        });
    }
    
    // Limpiar al salir
    window.addEventListener('beforeunload', cleanup);
    
    // API Pública
    return {
        init: init,
        cleanup: cleanup,
        actualizar: iniciarActualizacion,
        detener: detenerActualizacion,
        setUpdateInterval: (ms) => { config.updateInterval = ms; },
        getConfig: () => ({ ...config })
    };
})();

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', MoraRealTime.init);

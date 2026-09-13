/**
 * BÚSQUEDA DE CLIENTES - VERSIÓN 2.0 (LIMPIA)
 * 
 * Una sola fuente de verdad para búsqueda de clientes
 * - Sin conflictos con otros scripts
 * - Sin duplicados
 * - Performance optimizado con debounce
 * - Compatible con todos los navegadores
 * 
 * Uso:
 *   new ClientSearch('#clientSearchInput', '#clientSearchResults')
 */

class ClientSearch {
    constructor(inputSelector, resultsSelector) {
        this.input = document.querySelector(inputSelector);
        this.resultsContainer = document.querySelector(resultsSelector);
        this.debounceTimer = null;
        this.debounceDelay = 300; // ms - espera 300ms antes de buscar
        this.currentResults = [];
        this.isSearching = false;
        
        if (this.input && this.resultsContainer) {
            console.log('✅ ClientSearch inicializado');
            this.attachEventListeners();
        } else {
            console.warn('⚠️ ClientSearch: No se encontraron elementos del DOM');
        }
    }
    
    /**
     * Adjunta listeners de eventos al input
     */
    attachEventListeners() {
        // Input event con debounce
        this.input.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                this.hideResults();
                return;
            }
            
            // Mostrar estado "buscando..."
            this.resultsContainer.innerHTML = '<li class="searching">Buscando...</li>';
            this.showResults();
            
            // Ejecutar búsqueda después del debounce
            this.debounceTimer = setTimeout(() => {
                this.search(query);
            }, this.debounceDelay);
        });
        
        // Click fuera para cerrar dropdown
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideResults();
            }
        });
        
        // Enter para seleccionar primer resultado
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const firstResult = this.resultsContainer.querySelector('li:not(.searching)');
                if (firstResult && firstResult.dataset.clientId) {
                    firstResult.click();
                }
            }
        });
        
        // Arrow keys para navegación (bonus)
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateResults(e.key === 'ArrowDown' ? 'down' : 'up');
            }
        });
    }
    
    /**
     * Realiza la búsqueda de clientes
     */
    search(query) {
        if (this.isSearching) return;
        
        this.isSearching = true;
        console.log(`🔍 Buscando: ${query}`);
        
        fetch(`/api/clientes/search/?q=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(data => {
                this.currentResults = data.results || [];
                if (data.success) {
                    this.renderResults(this.currentResults);
                } else {
                    this.showError(data.error || 'Error en búsqueda');
                }
            })
            .catch(error => {
                console.error('❌ Error en búsqueda:', error);
                this.showError('Error al conectar con servidor');
            })
            .finally(() => {
                this.isSearching = false;
            });
    }
    
    /**
     * Renderiza los resultados en el dropdown
     */
    renderResults(results) {
        if (results.length === 0) {
            this.showError('No se encontraron resultados');
            return;
        }
        
        // Limpiar resultados previos
        this.resultsContainer.innerHTML = '';
        
        // Agregar nuevos resultados (máximo 20)
        results.slice(0, 20).forEach((client, index) => {
            const li = document.createElement('li');
            li.setAttribute('role', 'option');
            li.setAttribute('aria-selected', 'false');
            li.dataset.clientId = client.id;
            li.dataset.index = index;
            
            // Formato: "Nombre - Cédula"
            li.innerHTML = `
                <strong>${this.escapeHtml(client.nombre)}</strong>
                <span class="text-muted ms-2">CI: ${this.escapeHtml(client.cedula)}</span>
            `;
            
            li.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectClient(client);
            });
            
            li.addEventListener('hover', () => {
                li.classList.add('active');
            });
            
            this.resultsContainer.appendChild(li);
        });
        
        this.showResults();
        console.log(`✅ ${results.length} resultados encontrados`);
    }
    
    /**
     * Selecciona un cliente del dropdown
     */
    selectClient(client) {
        console.log(`✅ Cliente seleccionado: ${client.nombre} (${client.id})`);
        
        // Actualizar input
        this.input.value = client.nombre;
        
        // Trigger custom event para que otros scripts escuchen
        const event = new CustomEvent('clientSelected', {
            detail: client,
            bubbles: true
        });
        this.input.dispatchEvent(event);
        
        // También trigger change event (para formularios)
        const changeEvent = new Event('change', { bubbles: true });
        this.input.dispatchEvent(changeEvent);
        
        // Guardar ID en input (útil si luego se envía formulario)
        this.input.dataset.clientId = client.id;
        
        // Limpiar resultados
        this.hideResults();
    }
    
    /**
     * Navega entre resultados con arrow keys
     */
    navigateResults(direction) {
        const items = this.resultsContainer.querySelectorAll('li:not(.searching):not(.error)');
        if (items.length === 0) return;
        
        const current = this.resultsContainer.querySelector('li.active');
        let nextIndex = 0;
        
        if (current) {
            const currentIndex = Array.from(items).indexOf(current);
            nextIndex = direction === 'down' 
                ? (currentIndex + 1) % items.length 
                : (currentIndex - 1 + items.length) % items.length;
        }
        
        items.forEach(item => item.classList.remove('active'));
        items[nextIndex].classList.add('active');
        items[nextIndex].scrollIntoView({ block: 'nearest' });
    }
    
    /**
     * Muestra los resultados
     */
    showResults() {
        this.resultsContainer.classList.add('active');
        this.resultsContainer.setAttribute('role', 'listbox');
    }
    
    /**
     * Oculta los resultados
     */
    hideResults() {
        this.resultsContainer.classList.remove('active');
    }
    
    /**
     * Muestra mensaje de error
     */
    showError(message) {
        this.resultsContainer.innerHTML = `<li class="error text-danger">${message}</li>`;
        this.showResults();
    }
    
    /**
     * Escapa caracteres HTML para seguridad
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

/**
 * Inicializar cuando el DOM esté listo
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeClientSearch);
} else {
    initializeClientSearch();
}

function initializeClientSearch() {
    // Buscar elementos de búsqueda en el DOM
    const searchInputs = document.querySelectorAll('[data-client-search="true"]');
    
    searchInputs.forEach(input => {
        const resultsId = input.dataset.resultsSelector || '#clientSearchResults';
        const resultsElement = document.querySelector(resultsId);
        
        if (resultsElement) {
            window[`clientSearch_${input.id}`] = new ClientSearch(`#${input.id}`, resultsId);
        }
    });
    
    // Fallback: si hay input/results con IDs estándar, inicializar también
    if (document.querySelector('#clientSearchInput') && document.querySelector('#clientSearchResults')) {
        window.clientSearch = new ClientSearch('#clientSearchInput', '#clientSearchResults');
    }
    
    console.log('✅ ClientSearch v2.0 inicializado completamente');
}

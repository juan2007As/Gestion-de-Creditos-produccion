/**
 * Posicionamiento dinámico para dropdowns de búsqueda
 * Funciona con todos los dropdowns position: fixed en el DOM
 */

function posicionarDropdown(inputElement, dropdownElement) {
    if (!inputElement || !dropdownElement) return;
    
    const rect = inputElement.getBoundingClientRect();
    const scrollLeft = window.scrollX || document.documentElement.scrollLeft;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    
    dropdownElement.style.position = 'fixed';
    dropdownElement.style.top = (rect.bottom + 5) + 'px';
    dropdownElement.style.left = rect.left + 'px';
    dropdownElement.style.width = rect.width + 'px';
    dropdownElement.style.zIndex = '10000';
}

/**
 * Configurar listeners para actualizar posición en scroll y resize
 */
function setupDropdownPositioning(inputElement, dropdownElement) {
    if (!inputElement || !dropdownElement) return;
    
    // Actualizar en scroll
    window.addEventListener('scroll', () => {
        if (dropdownElement.style.display !== 'none') {
            posicionarDropdown(inputElement, dropdownElement);
        }
    }, true);
    
    // Actualizar en resize
    window.addEventListener('resize', () => {
        if (dropdownElement.style.display !== 'none') {
            posicionarDropdown(inputElement, dropdownElement);
        }
    });
    
    // Actualizar cuando se muestre el dropdown
    const observer = new MutationObserver(() => {
        if (dropdownElement.style.display !== 'none') {
            posicionarDropdown(inputElement, dropdownElement);
        }
    });
    
    observer.observe(dropdownElement, {
        attributes: true,
        attributeFilter: ['style']
    });
}

/**
 * Función para formatear números con formato colombiano
 * Convierte 1234567.89 a $1.234.567,89
 * @param {number} valor - El número a formatear
 * @param {boolean} incluirSimbolo - Si debe incluir el símbolo $ (default: true)
 * @returns {string} - Número formateado con formato colombiano
 */
function formatearMonedaColombia(valor, incluirSimbolo = true) {
    if (valor === null || valor === undefined) {
        return incluirSimbolo ? '$0,00' : '0,00';
    }
    
    try {
        // Convertir a número
        valor = parseFloat(valor);
        
        if (isNaN(valor)) {
            return incluirSimbolo ? '$0,00' : '0,00';
        }
        
        // Usar Intl.NumberFormat para formato colombiano
        const formateado = new Intl.NumberFormat('es-CO', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(valor);
        
        return incluirSimbolo ? `$${formateado}` : formateado;
    } catch (error) {
        console.error('Error formateando moneda:', error);
        return incluirSimbolo ? '$0,00' : '0,00';
    }
}

/**
 * Función alternativa usando lógica de reemplazo (compatible con navegadores antiguos)
 * @param {number} valor - El número a formatear
 * @param {boolean} incluirSimbolo - Si debe incluir el símbolo $ (default: true)
 * @returns {string} - Número formateado con formato colombiano
 */
function formatearMonedaColombia_Legacy(valor, incluirSimbolo = true) {
    if (valor === null || valor === undefined) {
        return incluirSimbolo ? '$0,00' : '0,00';
    }
    
    try {
        valor = parseFloat(valor);
        if (isNaN(valor)) {
            return incluirSimbolo ? '$0,00' : '0,00';
        }
        
        // Formato con 2 decimales
        const partes = valor.toFixed(2).split('.');
        const enteros = partes[0];
        const decimales = partes[1];
        
        // Agregar separadores de miles
        const enterosFormateado = enteros.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        const resultado = enterosFormateado + ',' + decimales;
        
        return incluirSimbolo ? `$${resultado}` : resultado;
    } catch (error) {
        console.error('Error formateando moneda:', error);
        return incluirSimbolo ? '$0,00' : '0,00';
    }
}

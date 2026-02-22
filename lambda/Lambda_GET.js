import https from 'https';

/**
 * ============================================================================
 * LAMBDA GENÉRICA PARA CONSUMIR SERVICIOS REST GET
 * ============================================================================
 * 
 * CONFIGURACIÓN:
 * - Cambiar CONFIG con el endpoint, apikey, etc.
 * - Headers se ajustan automáticamente según lo requerido
 * 
 * EJEMPLO DE USO:
 * {
 *   "numeroDocumento": "5783822",
 *   "periodoFinal": "2302",
 *   "periodoInicial": "2001",
 *   "tipoDocumento": "1",
 *   "token": "tu_token_aqui"
 * }
 */

// ============================================================================
// CONFIGURACIÓN GENERAL
// ============================================================================

const CONFIG = {
    HOSTNAME: 'integracionesqa.comfama.com',
    PORT: 443,
    PATH: '/comfama/cuotamonetaria/api/v1/consultaCuotaMonetaria',
    APIKEY: '0WOZZjFs89JAtlWfVyfV4wXe0l98iwJ3EWLaj3lb',
    TIMEOUT: 30000,
    CONTENT_TYPE: 'application/json'  // GET JSON
};

// ============================================================================
// HANDLER PRINCIPAL
// ============================================================================

export const handler = async (event) => {
    try {
        // CAMBIAR: Extraer el token, cookie y los parámetros de query
        const { token, cookie, ...queryParams } = event;

        if (!token) {
            return {
                statusCode: 400,
                error: 'Parámetro faltante: token'
            };
        }

        // Construir query string
        const queryString = Object.entries(queryParams)
            .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
            .join('&');

        // Hacer petición GET
        const response = await makeGetRequest(queryString, token, cookie);

        // Parsear respuesta
        let parsedResponse;
        try {
            parsedResponse = JSON.parse(response);
        } catch (e) {
            // Si no es JSON, devolver como string
            parsedResponse = response;
        }

        return {
            statusCode: 200,
            data: parsedResponse
        };

    } catch (error) {
        return {
            statusCode: 500,
            error: error.message
        };
    }
};

// ============================================================================
// PETICIÓN HTTPS GET
// ============================================================================

/**
 * Realiza la petición HTTPS GET
 */
function makeGetRequest(queryString, authToken, sessionCookie) {
    return new Promise((resolve, reject) => {
        const fullPath = `${CONFIG.PATH}?${queryString}`;

        const headers = {
            'Authorization': `Bearer ${authToken}`,
            'Accept': CONFIG.CONTENT_TYPE,
            'User-Agent': 'AWS-Lambda-Client'
        };

        // Agregar cookie si existe
        if (sessionCookie) {
            headers['Cookie'] = sessionCookie;
        }

        const options = {
            hostname: CONFIG.HOSTNAME,
            port: CONFIG.PORT,
            path: fullPath,
            method: 'GET',
            timeout: CONFIG.TIMEOUT,
            headers: headers
        };
        
        // DEBUG
        console.log('📤 URL:', `https://${CONFIG.HOSTNAME}${fullPath}`);
        console.log('📋 Headers:', JSON.stringify(options.headers, null, 2));

        const req = https.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                console.log('✅ Status:', res.statusCode);
                console.log('📨 Response:', data);
                
                if (res.statusCode === 403) {
                    reject(new Error(`HTTP 403 Forbidden - ${data}`));
                } else if (res.statusCode >= 400) {
                    reject(new Error(`HTTP ${res.statusCode} - ${data}`));
                } else {
                    resolve(data);
                }
            });
        });

        req.on('timeout', () => {
            req.destroy();
            reject(new Error(`Request timeout after ${CONFIG.TIMEOUT}ms`));
        });

        req.on('error', reject);

        req.end();
    });
}

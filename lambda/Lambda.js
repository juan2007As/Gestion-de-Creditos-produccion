import https from 'https';

/**
 * ============================================================================
 * LAMBDA GENÉRICA PARA CONSUMIR SERVICIOS SOAP
 * ============================================================================
 * 
 * CONFIGURACIÓN:
 * - Cambiar CONFIG con el endpoint, apikey, etc.
 * - Cambiar buildSoapEnvelope() con los tags SOAP necesarios
 * - Headers se ajustan automáticamente según lo requerido
 * 
 * EJEMPLO DE USO:
 * {
 *   "TIP_IDENT": "CO1N",
 *   "NUM_IDENT": "8110065381",
 *   "NUM_CREDITO": "0005114000052",
 *   "IV_CASTIGADA": "T",
 *   "token": "tu_token_aqui"
 * }
 */

// ============================================================================
// CONFIGURACIÓN GENERAL
// ============================================================================

const CONFIG = {
    HOSTNAME: 'integracionesqa.comfama.com',
    PORT: 443,
    PATH: '/sfin/SFIN-CRE-ConsultarPagoCuotaCredito',
    APIKEY: '0WOZZjFs89JAtlWfVyfV4wXe0l98iwJ3EWLaj3lb',
    TIMEOUT: 30000,
    CONTENT_TYPE: 'text/xml'  // SOAP
};

// ============================================================================
// HANDLER PRINCIPAL
// ============================================================================

export const handler = async (event) => {
    try {
        // CAMBIAR: Extraer el token y los datos del payload
        const { token, ...soapParams } = event;

        if (!token) {
            return {
                statusCode: 400,
                error: 'Parámetro faltante: token'
            };
        }

        // Construir SOAP envelope
        const soapBody = buildSoapEnvelope(soapParams);

        // Hacer petición SOAP
        const response = await makeSoapRequest(soapBody, token);

        // Parsear respuesta XML a JSON
        const parsedResponse = xmlToJson(response);

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
// CONSTRUIR SOAP ENVELOPE
// ============================================================================

/**
 * Construye el SOAP envelope con los parámetros recibidos
 * CAMBIAR: Los tags dentro del SOAP según lo que espere el servicio
 */
function buildSoapEnvelope(params) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:comfama.com.co:integra_recaudo:consulta_saldo_deuda_ipscd038_01">
   <soapenv:Header/>
   <soapenv:Body>
      <urn:INTEGRA_RECAUDO_Consulta_Saldo_Deuda_MT>
         <TIP_IDENT>${params.TIP_IDENT}</TIP_IDENT>
         <NUM_IDENT>${params.NUM_IDENT}</NUM_IDENT>
         <NUM_CREDITO>${params.NUM_CREDITO}</NUM_CREDITO>
         <IV_CASTIGADA>${params.IV_CASTIGADA}</IV_CASTIGADA>
      </urn:INTEGRA_RECAUDO_Consulta_Saldo_Deuda_MT>
   </soapenv:Body>
</soapenv:Envelope>`;
}

// ============================================================================
// PETICIÓN HTTPS SOAP
// ============================================================================

/**
 * Realiza la petición HTTPS POST para SOAP
 */
function makeSoapRequest(soapBody, authToken) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: CONFIG.HOSTNAME,
            port: CONFIG.PORT,
            path: CONFIG.PATH,
            method: 'POST',
            timeout: CONFIG.TIMEOUT,
            headers: {
                'Content-Type': `${CONFIG.CONTENT_TYPE}; charset=UTF-8`,
                'Content-Length': Buffer.byteLength(soapBody),
                'Authorization': `Bearer ${authToken}`,
                'apikey': CONFIG.APIKEY,
                'SOAPAction': ''
                // CAMBIAR: Headers adicionales si es necesario
            }
        };
        
        // DEBUG
        console.log('📤 URL:', `https://${CONFIG.HOSTNAME}${CONFIG.PATH}`);
        console.log('📋 Headers:', JSON.stringify(options.headers, null, 2));
        console.log('📦 SOAP Request:', soapBody);

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

        req.write(soapBody);
        req.end();
    });
}

// ============================================================================
// PARSER XML A JSON
// ============================================================================

/**
 * Convierte XML SOAP a JSON extrayendo valores
 */
function xmlToJson(xmlString) {
    const json = {};
    const tagRegex = /<([a-zA-Z0-9:_-]+)(?:\s[^>]*)?>([^<]*)<\/\1>|<([a-zA-Z0-9:_-]+)(?:\s[^>]*)?\/>/g;
    let match;

    while ((match = tagRegex.exec(xmlString)) !== null) {
        const tag = match[1] || match[3];
        const content = match[2] ? match[2].trim() : '';

        if (content && !tag.includes('Envelope') && !tag.includes('Header') && !tag.includes('Body') && !tag.includes('soapenv') && !tag.includes('soap:')) {
            const cleanTag = tag.split(':').pop();
            json[cleanTag] = content;
        }
    }

    return json;
}

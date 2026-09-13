# Reglas de Seguridad

> Plantilla base. Especializar según el stack y el tipo de datos que maneje el proyecto (¿hay pagos? ¿datos médicos? ¿menores de edad?) en la Fase 2.
>
> Perfil mínimo: **P0**. Las reglas marcadas `[P2]`/`[P3]` aplican desde ese perfil (ver [[README]]).
>
> Archivos hermanos: [[identity-rules]] (quién eres y qué puedes tocar), [[audit-rules]] (quién hizo qué), [[compliance-rules]] (qué te obliga la ley), [[config-rules]] (secretos), [[dependencies-rules]] (código de terceros). Este archivo cubre el resto de la superficie de ataque.

## Principios no negociables

1. **Ningún secreto (API key, contraseña, token) en el código ni en el repositorio.** Siempre en variables de entorno o gestor de secretos, con `.env` en `.gitignore` desde el primer commit. Ver [[config-rules]] para rotación y para el procedimiento ante filtración.
2. **Toda entrada de usuario es hostil hasta que se demuestre lo contrario.** Validar tipo, longitud, formato y rango en el servidor. Sanitizar antes de usar en queries, comandos, o renderizado (prevención de SQL injection, XSS, command injection).
3. **Autenticación y autorización son cosas distintas** — verificar ambas en cada acción sensible: ¿sé quién eres? y ¿puedes hacer esto específicamente? El detalle completo está en [[identity-rules]].
4. **Contraseñas nunca en texto plano** — hash con algoritmo apto para contraseñas (argon2id/bcrypt/scrypt), nunca MD5/SHA1 solos.
5. **HTTPS siempre en producción**, sin excepción, incluidas las llamadas entre servicios internos si cruzan red pública.
6. **Principio de menor privilegio** en todo: permisos de base de datos, roles de usuario, scopes de API keys de terceros — dar solo el acceso mínimo necesario, nunca "admin por comodidad".
7. **La seguridad no se apoya en que nadie lo sepa.** Una URL difícil de adivinar, un ID largo o un endpoint no documentado no son protección. Si funciona porque nadie lo ha encontrado todavía, no funciona.

## Validación de entrada: dónde falla realmente

8. **Lista blanca antes que lista negra.** Se declara qué está permitido, no qué está prohibido. Toda lista de prohibidos se puede rodear.
9. **Consultas parametrizadas siempre.** Nunca se construye una consulta concatenando texto, ni siquiera "porque este valor viene de un desplegable". Lo mismo aplica a nombres de columna o de tabla dinámicos: se validan contra una lista cerrada.
10. **Asignación masiva (mass assignment)**: nunca se vuelca directamente el cuerpo de una petición sobre una entidad. Se declaran explícitamente los campos aceptados, o un usuario podrá enviar `{"rol": "admin"}` en su formulario de perfil.
11. **Path traversal**: ninguna ruta de archivo se construye con entrada del usuario sin normalizar y comprobar que el resultado sigue dentro del directorio permitido.
12. **SSRF**: ninguna petición saliente se hace a una URL proporcionada por el usuario sin validar el destino contra una lista blanca, bloqueando IPs internas y de metadatos del proveedor cloud, y **volviendo a validar tras cada redirección**. Es la vía habitual para leer las credenciales de la instancia.
13. **Redirección abierta**: los destinos de redirección tras login o tras una acción se validan contra rutas propias conocidas — si no, sirven para montar phishing con tu dominio.
14. **Deserialización**: nunca se deserializa contenido no confiable en formatos que puedan instanciar objetos o ejecutar código. Se usan formatos de datos puros y se validan contra un schema.
15. **XML**: si se procesa XML, entidades externas desactivadas (XXE).
16. **Expresiones regulares** aplicadas a entrada del usuario: cuidado con las que tienen retroceso catastrófico (ReDoS) — una cadena de 40 caracteres puede bloquear un núcleo durante minutos.
17. **Límites en todo**: tamaño de petición, número de elementos en una lista, profundidad de anidamiento, longitud de cada campo. Sin límites, la validación correcta se convierte en denegación de servicio.

## Salida y renderizado

18. **Escapado según el contexto de destino**, no genérico: HTML, atributo, URL, JavaScript y SQL escapan distinto. Aplicar el escapado equivocado es no aplicarlo.
19. Nunca se inserta HTML crudo proveniente del usuario. Si el producto lo exige (un editor de texto enriquecido), se sanitiza con una librería mantenida y una lista blanca de etiquetas y atributos — nunca con una expresión regular propia.
20. **[P1]** Cabeceras de seguridad configuradas explícitamente: `Content-Security-Policy` (la defensa de fondo contra XSS), `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, y control de `frame-ancestors` contra clickjacking.
21. Las respuestas de error no revelan versiones, rutas de archivos, consultas ni trazas. Ver [[observability-rules]].

## Sesiones, CSRF y frontend

22. **[P1]** Si la autenticación usa cookies, hay protección CSRF explícita (token sincronizador o `SameSite` estricto correctamente aplicado, entendiendo sus límites). Ver [[identity-rules]] §2 Sesiones y tokens.
23. Ningún secreto vive en el frontend. Todo lo que se envía al navegador es público, aunque esté ofuscado o minificado. Una clave de API en el bundle es una clave publicada.
24. La lógica de autorización vive en el servidor. Ocultar un botón no protege el endpoint.
25. **[P2]** Los recursos de terceros cargados en el navegador (scripts de CDN) llevan verificación de integridad, o se sirven desde el propio dominio. Ver [[dependencies-rules]] §6 Código que no es una dependencia declarada.

## Archivos subidos por el usuario

26. Validar **tipo real** (por contenido, no por extensión ni por lo que declare el cliente), tamaño máximo, y número de archivos.
27. El archivo se guarda con un **nombre generado por el sistema**, nunca con el nombre que envió el usuario.
28. **[P1]** Se sirve desde un dominio o subdominio **sin sesión ni cookies**, con `Content-Disposition` y `Content-Type` forzados, y desde una ruta donde el servidor no ejecute nada. Un HTML o un SVG subido y servido en tu dominio principal es XSS con acceso a la sesión de quien lo abra.
29. **[P1]** El almacenamiento no es público por defecto: acceso mediante **URLs firmadas con expiración**, y comprobando autorización antes de firmarlas. Un bucket público es la fuga de datos más común que existe.
30. **[P3]** Análisis antivirus de los archivos subidos si se comparten entre usuarios.

## Criptografía

31. **Nunca criptografía propia.** Ni el algoritmo, ni el modo, ni el relleno, ni "un cifrado sencillito para esto". Se usan las primitivas de alto nivel de una librería reconocida.
32. Se distingue: **hash** (irreversible, para contraseñas y verificación), **cifrado** (reversible, con clave) y **codificación** (base64 — no protege nada). Confundirlas es un fallo grave y frecuente.
33. La aleatoriedad para tokens, identificadores de sesión y códigos viene de un generador **criptográficamente seguro**, nunca del generador de números aleatorios general del lenguaje.
34. **[P1]** TLS con versiones modernas, certificados válidos y **renovación automatizada y monitorizada** ([[operations-rules]] §6 Continuidad: lo que caduca en silencio). La verificación de certificados nunca se desactiva "para que funcione en local".
35. **[P2]** Cifrado en reposo: está decidido y documentado qué se cifra a nivel de campo por encima del cifrado del disco (normalmente identificadores oficiales, datos de salud, credenciales de terceros de clientes), y dónde viven las claves.
36. **[P3]** Las claves de cifrado se gestionan en un KMS, con rotación definida, y separadas de los datos que protegen. Una clave guardada junto a lo que cifra no protege de nada.

## Superficie de red e infraestructura

37. **[P1]** La base de datos, las colas y las cachés **no están expuestas a internet**. El acceso es desde la red privada o mediante túnel, nunca abierto "temporalmente" — nada dura tanto como lo temporal.
38. **[P1]** El panel de administración y las herramientas internas no son públicamente accesibles sin una capa adicional (red, VPN, restricción por IP, MFA obligatorio).
39. **[P2]** Cada entorno tiene sus propias credenciales y su propio aislamiento de red. Un compromiso en staging no debe dar acceso a producción.
40. **[P2]** Rate limiting global además del de los endpoints sensibles, y protección frente a abuso automatizado en los formularios públicos.

## Seguridad del propio desarrollo

41. **[P1]** MFA obligatorio en el repositorio, el proveedor cloud y todos los servicios críticos ([[operations-rules]] §5 Accesos y bus factor).
42. **[P1]** Rama principal protegida; los cambios entran revisados y con el pipeline en verde ([[release-rules]]).
43. **[P1]** Escaneo automático de secretos en el pipeline y en pre-commit.
44. **[P2]** Análisis estático de seguridad (SAST) integrado en el pipeline, con criterio decidido de qué bloquea.
45. Las máquinas de desarrollo no tienen credenciales de producción ([[config-rules]] §2 Secretos).
46. No se pegan secretos, datos de producción ni volcados de base de datos en herramientas de terceros — incluidas las de IA. Ver [[ai-rules]].

## Modelado de amenazas ligero (en el planteamiento y ante cada feature sensible)

47. Antes de construir algo con superficie de seguridad, tres preguntas concretas: **¿quién querría atacar esto y para qué?** (dinero, datos, sabotaje, reputación), **¿qué es lo más valioso que hay aquí?**, y **¿qué es lo peor que puede hacer un usuario legítimo pero malicioso?** — que casi siempre es más realista que el hacker externo.
48. **[P2]** Se identifican explícitamente los puntos de confianza: qué se asume verdadero sin comprobarlo. Cada uno de esos supuestos es una vulnerabilidad potencial y debe ser una decisión, no un descuido.

## Cuando algo va mal

49. **[P2]** Existe un contacto público para reportar vulnerabilidades y el compromiso de responder ([[compliance-rules]] §8 Brechas de seguridad).
50. **[P2]** Un fallo de seguridad detectado se trata como incidente según [[operations-rules]], y si hay datos personales implicados se activa **en paralelo** el procedimiento de brecha de [[compliance-rules]] — los plazos legales no esperan a que termines de arreglarlo.
51. Un secreto expuesto se considera comprometido aunque "solo lo vimos nosotros": se revoca primero y se limpia después ([[config-rules]] §2 Secretos).

## Antes de dar por cerrada cualquier tarea con superficie de seguridad

- ¿Hay algún dato sensible expuesto en logs, respuestas de error, o URLs?
- ¿Se validó la entrada en el servidor, no solo en el cliente?
- ¿Se verificó autorización a nivel de recurso específico, no solo autenticación general?
- ¿Algún secreto quedó hardcodeado por accidente?
- ¿Esta funcionalidad amplía la superficie expuesta a internet? ¿Hacía falta?
- ¿Qué es lo peor que puede hacer aquí un usuario registrado y malintencionado?
- ¿Estoy confiando en algo que no he comprobado (un valor del cliente, la respuesta de un tercero, un nombre de archivo)?

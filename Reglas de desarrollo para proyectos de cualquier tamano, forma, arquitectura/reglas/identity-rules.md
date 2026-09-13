# Reglas de Identidad, Sesiones y Permisos

> Perfil mínimo del archivo: **P1** (desde que haya más de un usuario). Marcas `[P2]`/`[P3]` indican reglas que solo aplican desde ese perfil.
>
> Distinto de [[security-rules]]: aquello es "que no te ataquen"; esto es "quién eres, cuánto duras dentro, y qué puedes tocar". Es la superficie donde más fallos reales y más caros aparecen, y por eso tiene archivo propio.

## 1. Autenticación

1. **Autenticar es una cosa y autorizar es otra** — nunca se resuelven en el mismo sitio ni con la misma comprobación. "Está logueado" no responde a "puede hacer esto".
2. La autenticación se resuelve en un **único punto del código**. Si hay dos formas distintas de "saber quién eres" en el proyecto, una de las dos va a tener el hueco.
3. Contraseñas: hash con algoritmo apto para contraseñas (argon2id preferido, bcrypt aceptable), nunca MD5/SHA solos, nunca cifrado reversible. Ver [[security-rules]].
4. **No revelar si una cuenta existe.** Login fallido, registro con email ya usado y recuperación de contraseña devuelven la misma respuesta genérica independientemente de si el usuario existe. Si el producto exige lo contrario por UX, se decide explícitamente con el usuario y se compensa con rate limiting agresivo.
5. Rate limiting y bloqueo progresivo en login, registro, recuperación y verificación — por cuenta **y** por IP, porque atacar mil cuentas una vez esquiva el límite por cuenta.
6. Comparaciones de secretos (tokens, códigos, firmas) en tiempo constante — nunca con comparación de cadenas normal, que filtra información por el tiempo de respuesta.
7. **[P2]** Si se usa un proveedor externo de identidad (OAuth, SSO), verificar siempre el token contra el proveedor o su firma — no confiar en lo que el cliente afirma sobre sí mismo.
8. **[P3]** MFA disponible, y **obligatorio** para cuentas con privilegios administrativos.

## 2. Sesiones y tokens

9. Toda sesión tiene **caducidad explícita**. Una sesión que no expira nunca es una credencial permanente que el usuario no sabe que tiene.
10. Toda sesión debe poder **revocarse desde el servidor**, tanto individualmente como en bloque ("cerrar sesión en todos los dispositivos"). Un JWT autocontenido sin lista de revocación no cumple esto — si se elige ese diseño, se decide conscientemente y se compensa con expiración corta.
11. Dónde vive el token es una decisión explícita con consecuencias:
    - Cookie `httpOnly` + `Secure` + `SameSite` → protegida de XSS, pero **obliga a protección CSRF**.
    - Cabecera de autorización desde memoria/localStorage → no necesita CSRF, pero es legible por cualquier XSS.

    Se elige una, se documenta en `CONTEXTO.md`, y se implementa la contramedida que le corresponde. No se mezclan las dos.
12. **Renovación de sesión en cada cambio de privilegio**: al iniciar sesión, al cambiar contraseña y al cambiar de rol se emite identificador de sesión nuevo (previene fijación de sesión).
13. Cambiar la contraseña o cerrar sesión **invalida los tokens existentes**, incluidos los de refresco. Si no, cambiar la contraseña tras un robo no sirve de nada.
14. Los tokens de refresco rotan en cada uso; reutilizar uno ya consumido se trata como indicio de robo y revoca toda la familia de sesiones.
15. Ningún token, identificador de sesión ni código de un solo uso viaja en una **URL** (queda en historiales, logs de servidor, cabeceras `Referer` y capturas de pantalla).

## 3. Registro, verificación y recuperación

16. Los tokens de verificación de email, recuperación de contraseña e invitación son: de **un solo uso**, con **expiración corta** (minutos u horas, no días), **aleatorios criptográficamente**, y se guardan **hasheados** en base de datos — no en claro.
17. Usar un token de recuperación invalida todos los demás pendientes de esa cuenta.
18. Está definido explícitamente qué puede hacer una cuenta **no verificada** y qué no. Si la respuesta es "todo", la verificación es decorativa.
19. **Cambiar el email de una cuenta requiere verificar el nuevo y notificar al antiguo.** Es el vector clásico de secuestro: si un atacante con la sesión abierta puede cambiar el email en silencio, se queda la cuenta para siempre.
20. Toda acción sensible sobre la propia cuenta (cambio de contraseña, de email, de MFA, cierre de cuenta) **notifica al usuario** por un canal que el atacante no controla, y queda registrada en [[audit-rules]].
21. Acciones críticas (cambiar contraseña, borrar cuenta, cambiar datos de pago) piden **reautenticación** aunque la sesión esté abierta.

## 4. Autorización y modelo de permisos

22. El modelo de permisos se **declara explícitamente** en un solo lugar (matriz de rol × acción × recurso), no se deduce leyendo condicionales repartidos por el código. Si nadie puede responder "¿qué puede hacer exactamente un rol X?" sin leer el código entero, el modelo no existe.
23. **Autorización a nivel de recurso concreto, siempre.** "Es un usuario autenticado" no autoriza a leer el pedido número 1234; hay que comprobar que ese pedido es suyo o que su rol lo permite. Esto es IDOR y es la vulnerabilidad más común en aplicaciones reales.
24. **Denegar por defecto.** Un endpoint, una acción o un campo nuevo empieza sin acceso y se abre explícitamente. Nunca al revés.
25. La autorización se decide **en el servidor**. El frontend oculta botones por UX; no es una medida de seguridad. Toda comprobación que solo existe en el cliente se asume ausente.
26. Los identificadores expuestos al exterior no deben ser secuenciales adivinables cuando eso permita enumerar recursos ajenos (usar UUID/ULID). Esto **no sustituye** a la comprobación de autorización — la complementa.
27. **[P2]** Escalada de privilegios: quién puede otorgar un rol está definido, y nadie puede otorgarse a sí mismo un rol superior al que tiene. El primer superadmin se crea por un proceso controlado (semilla, comando de administración), nunca por un endpoint público.
28. **[P2]** El acceso masivo a datos (exportaciones, listados sin filtro, informes) se autoriza aparte del acceso individual — poder ver un cliente no es poder descargar los 40.000.

## 5. Multi-tenancy (si el proyecto sirve a varias organizaciones)

29. **[P2]** El aislamiento entre tenants es una invariante del sistema, no una condición más en la query. Se aplica en una capa transversal (filtro obligatorio, RLS de base de datos, conexión por tenant) de forma que **olvidarla sea imposible**, no solo desaconsejado.
30. **[P2]** Existe al menos un test automático que verifica que un usuario del tenant A no puede leer ni modificar recursos del tenant B, para cada tipo de recurso principal. Ver [[testing-rules]].
31. **[P2]** Ninguna caché, índice de búsqueda, cola, log o fichero generado mezcla datos de tenants sin llevar el tenant como parte de la clave.

## 6. Impersonación y acceso de soporte

32. **[P2]** Si existe la función de "entrar como usuario" para soporte, se rige por: quién puede usarla está restringido y auditado; queda registrado el **actor real** además del usuario impersonado; el hecho es consultable por el usuario afectado; y hay acciones vetadas durante la impersonación (cambiar contraseña, borrar cuenta, operaciones de pago).
33. **[P2]** Ningún miembro del equipo accede a datos de un cliente concreto sin una razón registrada. "Miré por curiosidad" debe ser detectable en el audit log.

## 7. Cuentas de máquina y claves de API

34. **[P2]** Las credenciales de sistema (API keys, tokens de servicio) son entidades distintas de los usuarios humanos: tienen dueño, ámbito (scopes) mínimo, fecha de caducidad y pueden revocarse individualmente.
35. **[P2]** Se guardan hasheadas; se muestran en claro **una sola vez**, en el momento de crearlas.
36. **[P2]** Su uso queda en [[audit-rules]] igual que el de un humano — una acción hecha por una integración también tiene autor.

## 8. Ciclo de vida de la cuenta

37. Está definido explícitamente qué significa cada estado de una cuenta (activa, pendiente de verificar, suspendida, cerrada) y qué transiciones son válidas. Ver la regla de máquinas de estado en [[data-rules]].
38. **Suspender no es borrar.** Suspender corta el acceso conservando los datos; borrar es irreversible y activa las obligaciones de [[compliance-rules]].
39. Al cerrar una cuenta está decidido de antemano: qué pasa con el contenido que creó (se borra, se anonimiza, se transfiere), qué pasa con sus sesiones activas (se revocan todas, inmediatamente), y qué pasa en los **sistemas externos** donde también existe ese usuario (proveedor de pagos, email marketing, storage, índice de búsqueda). Ver [[compliance-rules]].
40. **[P2]** Si la cuenta es la única administradora de una organización, el sistema impide dejarla huérfana — o exige transferir la propiedad antes.

## Antes de dar por cerrada cualquier tarea que toque identidad o permisos

- ¿Se comprobó autorización sobre **este recurso concreto**, o solo que hay sesión?
- ¿Un usuario cualquiera podría llegar a este dato cambiando un ID en la URL?
- ¿Esta acción sensible queda registrada en [[audit-rules]] con actor, recurso y momento?
- ¿Qué pasa con esta sesión/token si el usuario cambia la contraseña ahora mismo?
- ¿Hay algún permiso nuevo que se abrió por defecto en vez de denegarse por defecto?
- **[P2]** ¿Esta query lleva el filtro de tenant, y es imposible escribirla sin él?

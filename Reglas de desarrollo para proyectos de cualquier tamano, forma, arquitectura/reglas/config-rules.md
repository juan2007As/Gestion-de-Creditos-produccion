# Reglas de Configuración, Secretos y Feature Flags

> Perfil mínimo del archivo: **P0** para las secciones 1 y 2 (aplican siempre); **P2** para gestión formal de secretos y flags.
>
> Tres cosas que se parecen y se gestionan distinto: **configuración** (cambia entre entornos, no es secreta), **secretos** (credenciales, nunca se leen ni se muestran) y **feature flags** (cambian en caliente, controlan comportamiento). Meterlas en el mismo saco es el origen de la mitad de los secretos filtrados.

## 1. Configuración

1. **La configuración se valida al arrancar.** Si falta una variable obligatoria o tiene un formato inválido, la aplicación **no arranca** y dice exactamente qué falta. Nunca se descubre a las tres semanas, en producción, cuando alguien pisa por primera vez ese camino del código.
2. La configuración se lee **una vez, en un módulo central y tipado**. No se accede a las variables de entorno directamente desde el resto del código: eso hace imposible saber qué configura realmente el proyecto sin leerlo entero.
3. **Ningún valor por defecto inseguro.** Un secreto, una URL de producción o un modo debug nunca tienen valor por defecto: o están definidos explícitamente o la aplicación falla. Un `secret_key` con valor por defecto es una puerta abierta que nadie ve.
4. `.env.example` se actualiza **en el mismo commit** que introduce una variable nueva, con una descripción de para qué sirve y un valor de ejemplo (nunca el real). Si el ejemplo está desactualizado, nadie puede levantar el proyecto sin preguntar.
5. La configuración no incluye lógica de negocio. Si el código pregunta "¿en qué entorno estoy?" para decidir **qué calcula**, eso es un bug: ver [[environments-rules]] §Diferencias esperadas y documentadas entre entornos. Preguntar por el entorno para decidir **a qué servicio se conecta** sí es legítimo.
6. Cambiar un valor de configuración compartida es un evento de **impacto cruzado**: se busca todo lo que lo lee antes de tocarlo (ver [[integrity-rules]] §Casos específicos de alto riesgo).
7. **[P2]** Está documentado qué configuración se puede cambiar en caliente y cuál exige reinicio o redespliegue — para que nadie cambie un valor y se quede esperando un efecto que no va a llegar.

## 2. Secretos

8. **Ningún secreto en el repositorio, nunca, ni en una rama, ni "temporalmente".** El historial de Git es permanente: una vez subido, se considera comprometido aunque se borre el commit.
9. Los secretos viven en variables de entorno o en un gestor de secretos, **separados por entorno**. Las credenciales de producción no existen en ninguna máquina de desarrollo. Nadie "prueba una cosita rápida" con la clave real.
10. Un secreto nunca aparece en: logs, mensajes de error, URLs, respuestas de API, el bundle del frontend, capturas de pantalla, ni el prompt de una IA. Si hay que registrar una referencia a él, se enmascara.
11. **Escaneo automático de secretos** en pre-commit y en CI. La revisión a ojo antes de commitear falla exactamente el día que hay prisa. Ver [[release-rules]].
12. **[P2]** Todo secreto tiene **rotación** definida: cada cuánto se rota, quién lo hace, y qué hay que reiniciar o redesplegar después. Un secreto que lleva tres años vivo es un secreto que ya no sabes quién conoce.
13. **[P2]** El sistema debe soportar **dos secretos válidos a la vez** durante una rotación (el viejo y el nuevo), o la rotación provoca caída y por eso nunca se hace.
14. **Procedimiento ante filtración de un secreto**, escrito de antemano y en este orden:
    1. **Revocar** el secreto comprometido en el proveedor — primero, antes que cualquier otra cosa.
    2. Emitir y desplegar el nuevo.
    3. **Auditar el uso** del secreto comprometido en el periodo de exposición: qué se hizo con él.
    4. Limpiar el rastro (reescribir historia, borrar del log) — **último**, y sabiendo que no reduce el riesgo, solo evita repetir el error.
    5. Registrar el incidente según [[operations-rules]], y evaluar si obliga a notificar según [[compliance-rules]].
15. **[P3]** Cifrado en reposo de los secretos en el gestor, con claves gestionadas por un KMS, y acceso a la lectura de secretos auditado (ver [[audit-rules]]).

## 3. Feature flags

16. **[P1]** Todo flag tiene, desde que se crea: **un dueño**, un motivo, y una **fecha de caducidad**. Un flag sin fecha de caducidad es una rama de lógica permanente que nadie entiende dentro de seis meses.
17. **[P1]** Los flags se limpian cuando cumplen su función. La deuda de flags muertos es acumulativa: cada uno duplica los caminos posibles del código y hace imposible razonar sobre el comportamiento real del sistema.
18. **[P1]** Se distingue el tipo de flag, porque tienen vidas distintas: **de despliegue** (temporal, se borra al terminar el rollout), **de experimento** (temporal, muere con el experimento), **operacional** (permanente, tipo interruptor de emergencia) y **de permiso/plan** (permanente, pero eso en realidad es [[identity-rules]], no un flag).
19. **[P1]** Un flag **no sustituye a la autorización**. Ocultar una funcionalidad con un flag no impide que alguien llame al endpoint.
20. **[P2]** Cambiar un flag en producción es un cambio en producción: queda auditado con quién y cuándo (ver [[audit-rules]] §2 Qué se audita siempre), y está claro cómo revertirlo.
21. **[P2]** El código debe comportarse de forma segura si el servicio de flags no responde: el valor por defecto ante fallo se define explícitamente y suele ser "como estaba antes".

## 4. Parámetros de negocio

22. **[P1]** Los valores de negocio que van a cambiar (precios, límites, comisiones, plazos, textos legales) no se hardcodean dispersos por el código, pero **tampoco se convierten automáticamente en configuración editable**: se decide conscientemente cuál merece ser editable y cuál es un cambio de código que debe pasar por revisión.
23. **[P2]** Cambiar un parámetro de negocio en caliente se audita y, cuando afecta a datos históricos (un precio, un porcentaje aplicado), **se versiona**: lo ya calculado conserva el valor que se aplicó en su momento, no se recalcula con el nuevo.

## Antes de dar por cerrada cualquier tarea que toque configuración

- ¿Añadí una variable nueva? ¿Está en `.env.example`, validada al arrancar y documentada?
- ¿Este valor tiene un valor por defecto que sería peligroso en producción?
- ¿Hay algún secreto que pueda acabar en un log, una URL o una respuesta de error?
- ¿Este flag nuevo tiene dueño y fecha de caducidad, o acabo de crear deuda invisible?
- ¿Quién más lee esta configuración que estoy cambiando?

# Reglas de Testing / QA

> Sin esto, las promesas de [[integrity-rules]] ("no rompo nada") no son verificables — quedan en fe.
>
> Perfil mínimo: **P0**. Las reglas marcadas `[P1]`/`[P2]`/`[P3]` aplican desde ese perfil (ver [[README]]).

## Principios no negociables

1. Toda funcionalidad con lógica de negocio no trivial lleva al menos un test que la cubra — no se considera "terminada" sin eso.
2. Un bug corregido lleva un test que reproduce el caso que falló, para que no vuelva a romperse silenciosamente en el futuro (test de regresión). **El test se escribe antes del arreglo y se comprueba que falla** — si no falla antes, no está probando lo que crees.
3. Los tests se corren antes de dar una tarea por cerrada — no se asume que "debería pasar", se verifica.
4. No se deshabilita ni se comenta un test que falla para "arreglarlo después" sin dejarlo explícitamente marcado y comunicado al usuario — un test apagado en silencio es peor que no tener test.
5. **Un test que no puede fallar no es un test.** Si al romper deliberadamente el código el test sigue en verde, está probando otra cosa (o nada).
6. Se testea el **comportamiento observable**, no la implementación interna. Un test que se rompe con cada refactor sin que cambie el comportamiento es un freno, no una red de seguridad.

## Qué priorizar (no todo necesita el mismo nivel)

7. Lógica de negocio y cálculos → tests unitarios siempre.
8. Endpoints/flujos críticos (auth, pagos, creación/edición de datos principales) → tests de integración.
9. Flujos de usuario clave de punta a punta (el "camino feliz" principal del producto) → al menos un test end-to-end si el proyecto lo justifica por tamaño.
10. UI puramente visual sin lógica → verificación manual/visual es aceptable, no todo requiere test automatizado.
11. **La cobertura es una señal, no un objetivo.** Un 90% alcanzado con tests que no comprueban nada es peor que un 50% sobre lo que de verdad importa, porque además da falsa confianza. Se persigue cubrir lo crítico, no subir el número.

## Lo que casi nunca se testea y es lo que más cuesta cuando falla

12. **[P1]** **Tests de autorización explícitos**: que el usuario A no puede leer, modificar ni borrar el recurso del usuario B. Se escribe para cada tipo de recurso principal. Es la vulnerabilidad más común en aplicaciones reales y la que menos aparece en las suites de tests, porque el camino feliz siempre usa el usuario correcto.
13. **[P2]** **Aislamiento entre tenants**, si el sistema es multi-organización ([[identity-rules]] §5 Multi-tenancy). Una fuga de datos entre clientes es el peor fallo posible de un SaaS.
14. **[P1]** **Los casos límite y de error**, no solo el camino feliz: entrada vacía, valor nulo, número negativo, texto muy largo, cero resultados, tercero caído, timeout, doble envío del mismo formulario.
15. **[P1]** **Idempotencia**: ejecutar dos veces la misma operación crítica y comprobar que el efecto ocurre una sola vez ([[api-rules]] §3 Escritura segura y reintentos).
16. **[P2]** **Migraciones**: se prueban aplicándolas sobre datos representativos, y se prueba la reversión si se declara reversible ([[data-rules]]).
17. **[P2]** **Concurrencia** en las operaciones donde importa (reservas, saldos, unicidad): al menos un test que ejecute dos operaciones simultáneas y verifique que el resultado es correcto.
18. **[P1]** Fechas, zonas horarias y dinero: casos de cambio de horario, año bisiesto, redondeo y monedas distintas. Ver [[data-rules]] sección 2.

## Fiabilidad y aislamiento de la suite

19. **[P1]** **Los tests son deterministas.** Un test intermitente se arregla o se elimina; **no se reintenta hasta que pase**. Reintentar entrena al equipo a ignorar los fallos, y el día que uno es real también se ignora. Ver [[release-rules]] §1 Puerta de calidad automatizada.
20. **[P1]** Los tests **no llaman a servicios externos reales**. Se usan dobles o servidores simulados. Un test que depende de internet falla por motivos ajenos y deja de significar nada.
21. **[P1]** Cada test crea su propio estado y no depende del orden de ejecución ni de lo que dejó otro. Si la suite solo pasa en un orden concreto, hay acoplamiento oculto.
22. **[P1]** Los tests no usan el reloj real cuando el tiempo importa: se inyecta. Un test que falla los días 31 o a medianoche es un test roto.
23. **[P1]** El entorno de test es **aislado**: nunca apunta a la base de datos de producción, nunca envía emails, SMS ni notificaciones reales, nunca ejecuta cobros reales. Ver [[environments-rules]].
24. **[P1]** **Los datos de test son sintéticos.** Nunca PII real de personas, ni emails o teléfonos reales — ni siquiera "los míos, que total soy yo". Ver [[data-rules]] §7 Operar sobre datos reales.

## Más allá de los tests automáticos

25. **[P1]** La prueba manual sigue siendo obligatoria donde el test automático no llega: verlo funcionando en el navegador o en el cliente real. "Compila y los tests pasan" no es lo mismo que "funciona". Ver [[front-rules]].
26. **[P2]** Cuando el rendimiento es un requisito real, se mide con volumen realista antes de que sea un problema. Un endpoint probado con 10 filas no dice nada sobre su comportamiento con 100.000.
27. **[P3]** Las funcionalidades críticas de seguridad se revisan además con análisis específico (SAST, revisión dirigida, o pruebas de intrusión según el perfil). Ver [[security-rules]].

## Antes de dar una tarea por cerrada

- ¿Existe un test que **falle** si este cambio se rompe en el futuro? ¿Lo he comprobado rompiéndolo?
- ¿Se corrieron los tests existentes y pasan? (verificado, no supuesto)
- ¿Un bug corregido tiene su test de regresión correspondiente?
- ¿Testé el camino de error, o solo el camino feliz?
- **[P1]** ¿Hay un test que compruebe que otro usuario **no** puede acceder a esto?
- **[P1]** ¿Algún test depende de la red, del reloj o del orden de ejecución?

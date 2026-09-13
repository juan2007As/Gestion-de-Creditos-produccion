# Reglas de Dependencias y Cadena de Suministro

> Perfil mínimo del archivo: **P0** para las secciones 1 y 2; **P2** para auditoría automatizada y política de licencias.
>
> La mayor parte del código que corre en producción no lo escribiste tú. Cada dependencia es código de un desconocido ejecutándose con tus permisos, sobre tus datos. Eso merece reglas propias.

## 1. Antes de añadir una dependencia

1. **Se evalúa antes de instalar, no después.** Las preguntas mínimas: ¿resuelve algo que no puedo resolver razonablemente sin ella?, ¿está mantenida (último commit, issues abiertos, número de mantenedores)?, ¿qué arrastra consigo?, ¿qué pasa si mañana la abandonan?
2. **Se verifica que el paquete es el que se cree.** Nombre exacto, autor u organización esperados, y enlace al repositorio real. El typosquatting y las suplantaciones de nombre son un vector activo, y una IA puede sugerir con total seguridad un paquete que no existe o que existe pero es otro. **Nunca se instala un nombre de paquete sugerido sin comprobar que corresponde al proyecto real.**
3. **Una dependencia de una función no es una dependencia.** Añadir un paquete entero, con su árbol de subdependencias y su superficie de ataque, para ahorrar diez líneas es un mal negocio.
4. Se prefiere lo que ya trae el lenguaje o el framework antes que traer algo nuevo. Cada dependencia es una decisión que alguien tendrá que mantener durante años.
5. **[P2]** Se revisa el número de subdependencias que arrastra. Un paquete con doscientas dependencias transitivas son doscientos autores con acceso efectivo a tu build.
6. **[P2]** Se prefieren dependencias con múltiples mantenedores frente a las de una sola persona, y se evita depender de forma crítica de un paquete sin actividad reciente.

## 2. Fijado de versiones y reproducibilidad

7. **El lockfile se commitea siempre.** Sin él, dos personas o dos despliegues instalan versiones distintas y el "en mi máquina funciona" es literalmente cierto.
8. **Nunca `latest` ni rangos abiertos en producción.** Un despliegue debe instalar exactamente lo mismo hoy que dentro de tres meses. Una actualización llega porque alguien decide actualizar, no porque tocaba redesplegar.
9. Las imágenes base de contenedores también se fijan (por versión concreta o por digest), no a una etiqueta móvil.
10. **[P2]** Las dependencias de desarrollo se separan de las de producción, y el artefacto desplegado no incluye las de desarrollo.
11. **[P2]** Las herramientas de build y el runtime tienen versión fijada y declarada — el mismo problema aplica al compilador y al intérprete, no solo a las librerías.

## 3. Vulnerabilidades y actualización

12. **[P1]** Existe un escaneo automático de vulnerabilidades conocidas en el pipeline (ver [[release-rules]]), con un criterio decidido de **qué severidad bloquea la integración** y qué solo avisa.
13. **[P1]** Las alertas de vulnerabilidad se atienden con criterio, no en piloto automático: importa si la parte vulnerable se usa realmente y si es alcanzable desde entrada externa. Pero "no me afecta" es una conclusión que se argumenta, no un supuesto por pereza.
14. **[P1]** **Actualizar es una tarea calendarizada**, con cadencia definida ([[operations-rules]] §8 Mantenimiento planificado). Las dependencias no se congelan indefinidamente: cuanto más se espera, más doloroso y más arriesgado es el salto, hasta que se vuelve un proyecto en sí mismo.
15. **[P1]** Ninguna dependencia crítica se queda en una versión **fuera de soporte**. Esto incluye el lenguaje, el runtime y la base de datos, no solo las librerías. Una versión sin soporte no recibe parches de seguridad: es una vulnerabilidad futura garantizada.
16. **[P1]** Una actualización de dependencia es un cambio como cualquier otro: pasa por el pipeline y por [[integrity-rules]]. Las actualizaciones mayores se hacen de una en una, no diez a la vez, para que se sepa cuál rompió qué.
17. **[P2]** Cuando una dependencia se abandona, se registra en `DEUDA-TECNICA.md` con su plan de sustitución ([[evolution-rules]]) — no se descubre el problema el día que aparece un CVE sin parche.

## 4. Confianza en el proceso de instalación

18. **[P2]** Instalar una dependencia **ejecuta código** (scripts de instalación) en la máquina de quien instala y en el pipeline. Se instala desde fuentes conocidas, y el pipeline usa instalación desde el lockfile sin permitir su modificación automática.
19. **[P2]** Los registros de paquetes usados están declarados. Nunca se mezcla un registro interno con el público de forma que un paquete público con el mismo nombre pueda suplantar al interno (confusión de dependencias).
20. **[P3]** Existe un inventario de qué compone el artefacto desplegado (SBOM), para poder responder en minutos —y no en días— a "¿nos afecta esta vulnerabilidad que acaba de salir?".

## 5. Licencias

21. **[P2]** La licencia de cada dependencia es compatible con el uso previsto del proyecto. Una licencia copyleft fuerte en un producto propietario es un problema legal, no una molestia.
22. **[P2]** La comprobación de licencias está automatizada, con la lista de licencias aceptadas declarada. Descubrir esto en una auditoría o en una due diligence, con el producto ya construido, es carísimo.
23. **[P2]** Lo mismo aplica a fuentes tipográficas, iconos, imágenes y modelos: tienen licencia y también se comprueba.

## 6. Código que no es una dependencia declarada

24. Copiar y pegar código de internet, de la documentación de otro proyecto o generado por una IA **no elimina la cuestión de licencia ni la de seguridad** — solo la vuelve invisible. Se entiende lo que hace antes de incorporarlo, y si tiene origen y licencia identificables, se anota.
25. Las dependencias cargadas en el navegador desde un CDN externo son código de terceros ejecutándose en la sesión del usuario: se evitan cuando se puede, y si se usan, con verificación de integridad. Ver [[security-rules]].

## Antes de añadir o actualizar cualquier dependencia

- ¿Comprobé que este paquete existe, es el correcto y está mantenido, o solo confié en el nombre?
- ¿Merece la pena lo que me ahorra frente a lo que arrastra?
- ¿Está el lockfile actualizado y commiteado?
- ¿Esta actualización rompe algo? ¿Corrí el pipeline completo, no solo el build?
- ¿Alguna dependencia crítica del proyecto está ya fuera de soporte?

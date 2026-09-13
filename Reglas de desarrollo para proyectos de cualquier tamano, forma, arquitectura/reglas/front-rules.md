# Reglas de Frontend

> Plantilla base. Al generarse para un proyecto real, reemplazar [STACK], [BREAKPOINTS], etc. con las decisiones tomadas en la Fase 1 del planteamiento.

## Principios no negociables

1. **Ningún texto se sale de su contenedor.** Todo texto largo, nombre de usuario, título dinámico o dato externo debe manejar overflow explícitamente (`truncate`, `line-clamp`, `wrap`, scroll interno) — nunca asumir que el contenido siempre será corto. Probar mentalmente (o de verdad) con el texto más largo razonable antes de dar por terminado un componente.
2. **Responsive real, no solo "no se rompe".** Cada vista se valida en al menos: móvil pequeño (~360px), tablet (~768px) y desktop (~1440px). No basta con que no haya scroll horizontal — la jerarquía visual y la usabilidad deben mantenerse en cada tamaño.
3. **Coherencia visual estricta.** Un mismo tipo de elemento (botón primario, card, input, spacing entre secciones) se ve y comporta igual en todo el proyecto. Si se necesita una variante nueva, se documenta como tal, no se improvisa una vez y se olvida.
4. **Estados completos, siempre.** Todo componente que carga datos o depende de una acción del usuario debe definir explícitamente: estado vacío, estado de carga, estado de error, y estado con datos. No dejar ninguno "para después".
5. **Accesibilidad mínima real, no decorativa.** Contraste de color suficiente (AA como mínimo), elementos interactivos navegables por teclado, labels en inputs, alt en imágenes con significado. Esto no es opcional "si da tiempo".
6. **Feedback inmediato de toda acción.** Click, submit, error de validación: el usuario nunca debe quedarse sin saber si algo pasó. Loading states y confirmaciones son obligatorios en acciones que tardan o son irreversibles.

## Estructura y mantenibilidad

7. Un componente hace una cosa. Si un componente empieza a tener múltiples responsabilidades no relacionadas, se divide — pero no se fragmenta prematuramente sin necesidad real.
8. Nombrar componentes y archivos por lo que muestran/hacen, no por dónde están usados ("UserCard", no "Componente3").
9. Estilos centralizados en el sistema de diseño del proyecto (tokens de color, espaciado, tipografía) — valores mágicos sueltos (`padding: 13px`, colores hex sueltos) están prohibidos salvo excepción justificada.
10. Ningún componente nuevo se crea sin revisar primero si ya existe uno reutilizable que cumpla la necesidad (ver [[integrity-rules]]).

## El frontend no es una frontera de seguridad

11. **Ningún secreto vive en el frontend.** Todo lo que llega al navegador es público, por muy minificado que esté. Una clave de API en el bundle es una clave publicada ([[security-rules]] §Sesiones, CSRF y frontend).
12. **Ocultar un botón no es autorizar.** El frontend esconde lo que el usuario no puede hacer por claridad; quien decide es el servidor. Toda comprobación que solo existe en el cliente se asume ausente ([[identity-rules]] §4 Autorización y modelo de permisos).
13. La validación del cliente existe por UX (feedback inmediato), la del servidor por seguridad e integridad. Ambas, siempre, y no se confía nunca en la primera.
14. La UI no muestra más de lo que el usuario puede ver: si la API devuelve el objeto completo y el front oculta campos, esos campos ya se han filtrado ([[api-rules]] §1 Forma del contrato).

## Texto, idiomas y formatos

15. **[P1]** Ningún texto visible se escribe directamente en el componente. Todos los textos pasan por la capa de textos del proyecto desde el primer día, aunque solo haya un idioma. Añadir internacionalización después obliga a tocar cada archivo de la interfaz, y por eso casi nunca se hace.
16. **[P1]** Fechas, horas, números y monedas se formatean con la API de internacionalización de la plataforma según la configuración del usuario — nunca concatenando a mano.
17. **[P1]** **Las fechas se muestran en la zona horaria del usuario y se almacenan en UTC** ([[data-rules]] §2 Los dos temas que siempre se hacen mal). Y cuando la hora importa (una cita, un plazo), se indica la zona en pantalla: "18:00" sin contexto es ambiguo en cuanto hay dos usuarios en países distintos.
18. **[P2]** Si el proyecto va a soportar varios idiomas, el diseño lo contempla desde el principio: el mismo texto ocupa hasta un 40% más en otros idiomas, y hay idiomas que se leen de derecha a izquierda. Un diseño ajustado al milímetro en español se rompe entero al traducirlo.
19. **[P1]** La interfaz no asume formatos de nombre, dirección, teléfono ni código postal de un solo país si el producto es internacional.

## Accesibilidad (ampliación del punto 5)

20. **[P1]** Todo lo interactivo es alcanzable y operable **solo con teclado**, con un foco visible. Es la comprobación más rápida y la que más problemas reales detecta.
21. **[P1]** Se usa el elemento semántico correcto (un botón es un botón, no un `div` con un manejador de clic). El HTML semántico da accesibilidad casi gratis; simularlo con atributos ARIA es más trabajo y sale peor.
22. **[P1]** El color nunca es el único portador de información (un estado no se distingue solo por rojo o verde).
23. **[P1]** Los errores de formulario están asociados a su campo y son anunciables, no solo un texto rojo suelto.
24. **[P2]** En muchos contextos la accesibilidad es una **obligación legal**, no una mejora opcional ([[compliance-rules]] §7 Ámbitos con reglas propias).

## Rendimiento percibido

25. **[P1]** Hay un presupuesto de rendimiento declarado (tamaño de bundle y tiempo hasta que la pantalla es usable) y se comprueba, no se supone. Se valida además en una conexión y un dispositivo lentos, no solo en el equipo de desarrollo.
26. **[P1]** Las listas que pueden crecer se paginan o virtualizan; no se renderizan diez mil filas "porque en pruebas iban veinte".
27. **[P1]** Las imágenes se sirven dimensionadas y en formato adecuado, con espacio reservado para que la página no salte al cargar.
28. **[P1]** Toda acción que pueda enviarse dos veces (doble clic, reintento) está protegida en la interfaz **y** en el servidor ([[api-rules]] §3 Escritura segura y reintentos).

## Antes de dar por terminada cualquier tarea de front

- ¿Se ve bien en móvil, tablet y desktop?
- ¿Hay algún texto que pueda desbordarse con contenido real (no el de prueba corto)?
- ¿Los estados vacío/carga/error están cubiertos?
- ¿Es consistente con el resto de la UI existente, o introduce una variante no documentada?
- ¿Se probó de verdad en navegador, o solo se asumió que compila?
- ¿Se puede usar solo con el teclado?
- ¿Hay algún texto, formato de fecha o de número escrito a mano en el componente?
- ¿Estoy confiando en el cliente para algo que debería decidir el servidor?

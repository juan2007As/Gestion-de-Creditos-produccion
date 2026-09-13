# Reglas de Privacidad y Cumplimiento (Gestión de Créditos)

> **Aviso**: esto son reglas de ingeniería para no incumplir por descuido, no asesoramiento legal. El proyecto opera en Colombia (ver `CONTEXTO.md`) — el marco aplicable es la **Ley 1581 de 2012 (Habeas Data)** y normativa de la SIC, no el RGPD europeo. La decisión final sobre obligaciones legales es de un profesional del derecho colombiano; el trabajo de la IA es que el sistema **pueda** cumplir.
>
> No aplican en este proyecto: pagos con tarjeta (los pagos se registran manualmente, no hay tokenización de tarjeta — confirmado en `CONTEXTO.md`), menores de edad como usuarios del producto, datos de salud/biométricos.

## 1. Inventario: qué datos personales maneja este proyecto

1. Datos personales identificados en `Cliente`: `cedula`, `nombre`, `celular`, `email`, más el historial derivado (`total_prestado_historico`, `tasa_cumplimiento`, `dias_mora_promedio`, `etiqueta_cliente`) — esto último es un **perfilado automático** del comportamiento de pago de una persona, con más sensibilidad de la que parece a primera vista.
2. No existe un inventario formal escrito más allá de este archivo — este es el primero. Actualizarlo en el mismo cambio que se agregue un campo personal nuevo a `Cliente`, `Prestamo` o modelos relacionados.
3. `ListaNegra` también es un dato personal sensible por naturaleza (marca a una persona como morosa) — mismo nivel de cuidado que los datos financieros.

## 2. Minimización

4. No se recoge un dato "por si acaso" — cada campo de `Cliente` tiene un uso concreto en el cálculo de scoring/mora. Antes de agregar un campo nuevo, confirmar que hace falta de verdad.

## 3. Consentimiento

5. Los clientes de la operación de crédito no tienen cuenta ni interfaz propia (confirmado en `CONTEXTO.md`) — el consentimiento para tratar sus datos se gestiona fuera del sistema (contrato de préstamo en papel/físico, presumiblemente). Si en algún momento el sistema empieza a recoger consentimiento digital, aplican las reglas estándar: registrar qué aceptó, cuándo, y qué versión del texto.

## 4. Derechos del titular (Habeas Data)

6. **Hoy no está implementado ningún mecanismo de acceso/rectificación/borrado a pedido de un cliente** — depende de que el dueño lo resuelva manualmente si algún cliente lo solicita. Deuda cajón 2.
7. **El borrado es un problema real hoy**: `Cliente` con `on_delete=CASCADE` hacia `Prestamo`/`Cuota`/`Pago` borra todo en cadena, sin soft-delete ni anonimización — si un cliente pide que se lo elimine, hoy la única opción es un borrado físico total que también destruye el historial contable de esos préstamos (que probablemente hay que conservar por motivos fiscales). Esto necesita decidirse antes de que llegue la primera solicitud real, no durante ella.

## 5. Retención

8. **No hay política de retención definida** para los datos de un cliente (activo, inactivo, o con préstamos ya liquidados hace años). Deuda cajón 2 — `DEUDA-TECNICA.md`.
9. Los backups (`.github/workflows/backup.yml`) retienen 30 días vía GitHub Actions artifacts — coordinar esa retención con la que se defina para los datos en sí cuando se escriba la política.
10. Los logs de auditoría (`HistorioCambios`/`AuditLog`) no tienen retención definida ni purga automática — crecen indefinidamente hoy.

## 6. Terceros

11. Tras retirar `lambda/` (integración Comfama), **no hay terceros activos** que reciban datos de clientes. Si se retoma esa integración o se agrega cualquier servicio nuevo que reciba datos de clientes (ej. un servicio de email transaccional, un scoring externo), se decide explícitamente con el dueño antes de conectar, no como detalle técnico.

## 7. Decisiones automatizadas

12. `etiqueta_cliente` (BUENO/MEDIO/MALO/SIN_HISTORIAL) y la lista negra automática son decisiones automatizadas que afectan si a una persona se le presta dinero o no. Deben poder explicarse (qué reglas la generaron) y tener revisión humana antes de una decisión final — confirmar que un operario siempre puede anular manualmente una etiqueta o salida de lista negra, no solo el sistema.

## Antes de dar por cerrada cualquier tarea que toque datos de clientes

- ¿Este dato nuevo es personal? ¿De verdad hace falta guardarlo?
- Si un cliente pidiera que se lo elimine hoy, ¿qué pasaría exactamente? (hoy: cascada total, sin plan)
- ¿Este dato acaba en un log, una exportación de Excel, o un tercero nuevo sin que se haya decidido conscientemente?

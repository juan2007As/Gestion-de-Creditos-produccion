# Reglas de Evolución y Actualización (Gestión de Créditos)

## 1. El planteamiento original es el ancla

1. Toda feature nueva se contrasta contra `CONTEXTO.md` antes de construirse.
2. Ninguna feature se da por "planteada" solo porque el dueño la pidió en una frase — proporcional a su tamaño.

## 2. Revisión periódica de contexto

3. Cada cierto número de cambios significativos, revisar `CONTEXTO.md` y `reglas/` completo para detectar desactualización.
4. Si algo ya no aplica o se contradice, corregirlo ahí mismo.

## 3. Registro de deuda técnica

5. Todo atajo consciente se registra en `DEUDA-TECNICA.md` — ya poblado con 16+ ítems reales tras la auditoría de adopción (Fases A0-A4).
6. Antes de tomar un atajo nuevo, se avisa al dueño explícitamente.
7. La deuda se revisa en la misma cadencia que la revisión de contexto — preguntar si alguna ya vale la pena pagar. Ejemplo real: el bug de `total_a_pagar()` (cajón 1 #1) debería ser de las primeras en revisarse la próxima vez que se toque cálculo de cuotas.

## 4. Definition of Done por feature

### Las 5 puertas (bloquean el cierre, sin excepción)

Las mismas de [[00-CORE]]:

8. **Seguridad**: sin hueco de autorización, validación ni exposición.
9. **No rompe lo existente**: dependientes verificados.
10. **Verificado, no supuesto**: tests corridos y en verde (o probado de verdad).
11. **Rastro**: si puede fallar en producción, hay forma de enterarse — hoy este proyecto NO lo tiene del todo (cajón 1 #6, diferido por decisión del dueño). Mientras eso siga así, extremar la verificación manual en cambios sensibles.
12. **Nada oculto**: atajos registrados en `DEUDA-TECNICA.md`.

### Recordatorios (se revisan; se pueden diferir dejando constancia)

13. Estados completos, responsive, transacciones, idempotencia según toque.
14. `CONTEXTO.md` refleja lo que este cambio añade.
15. Si añade datos personales de clientes: inventariados y con retención — hoy sin definir (ver [[compliance-rules]]).
16. Si añade configuración: validada al arrancar y en `.env.example`.
17. Si añade una dependencia: `requirements.txt` con versión fijada (lockfile ya establecido en A4 — no romperlo agregando algo sin `==`).

## 4bis. Revisión del perfil del proyecto

18. El perfil (P3, fijado en A2) se revisa en cada auditoría periódica. Sube si aparecen más usuarios reales, más dinero, o regulación nueva aplicable.
19. Subir de perfil no se hace en silencio.

## 5. Prioridad bajo presión de tiempo

Orden de lo que NUNCA se sacrifica:

1. **Seguridad**.
2. **Integridad y no perder datos** — incluye backup verificado (`.github/workflows/backup.yml` corre diario y falla si no restaura).
3. **Funcionalidad correcta del camino principal**.
4. **Poder detectar que ha fallado** — reducible a mínimo, no a cero (aunque hoy ya esté reducido a casi cero por decisión explícita del dueño, cajón 1 #6).
5. **Cobertura de test** — reducible a lo crítico (autorización, cálculo de dinero).
6. **Pulido de UI/UX, refactor cosmético** — lo primero en ceder.

**Nunca aceptable, por mucha prisa**: commitear un secreto "temporalmente", ejecutar un cambio irreversible en producción sin backup verificado, o tocar un cálculo de dinero sin `Decimal`.

## 6. Cambios reversibles vs irreversibles

20. Antes de cualquier decisión, clasificarla.
21. Las difíciles de revertir se confirman siempre con el dueño: borrar/transformar datos de producción, reescribir historial de git ya en `origin`, cambiar de proveedor de hosting/DB, empezar a recoger una categoría nueva de datos personales.

## 7. Mantenimiento recurrente

22. La lista de tareas recurrentes vive en [[operations-rules]] §Recordatorios.
23. "Cuando haya tiempo" significa nunca — la factura se paga entera el día del incidente.

## 8. Aprender de los fallos — casos reales de este proyecto

> Esta sección es la que hace que el conjunto de reglas mejore con el uso. Estos son los primeros tres casos reales que la adopción (Fases A0-A4) ya dejó:

24. **Caso: `Cuota.total_a_pagar()` sumaba el interés original en vez del pendiente.** *¿Había una regla?* No había — se escribió en [[data-rules]] §2 y en [[00-CORE]] §12 con este caso pegado.
25. **Caso: `valida_propiedad_cliente`/`valida_propiedad_prestamo` comprobaban un campo (`usuario_creador`) que nunca existió en `Cliente`/`Prestamo`.** El `hasattr(...) else True` hacía que el chequeo pasara siempre. *¿Había una regla?* Sí, pero era ambigua: nada exigía que un decorador de seguridad tuviera un test que probara el caso negativo real (usuario B *no* debería poder). Se afiló en [[testing-rules]] (pendiente de generar) y se registró en [[identity-rules]].
26. **Caso: `tech_debt_fixes.py` se escribió para centralizar cálculos duplicados, pero nunca se conectó al código real — solo lo prueban sus propios tests.** *¿Había una regla?* No había una que exigiera verificar que una "solución a deuda técnica" esté realmente en el camino de ejecución, no solo probada de forma aislada. Nueva regla, en [[evolution-rules]] mismo: **cuando se declare resuelta una deuda técnica, se confirma con grep que el código viejo ya no existe o ya llama al nuevo — un módulo de reemplazo sin nadie importándolo no resolvió nada.**
27. La regla nueva lleva su caso pegado (ver arriba). Si en el futuro aparece un cuarto caso parecido, se afila aquí mismo.

## Checklist de cierre de cualquier ciclo de trabajo

- ¿`CONTEXTO.md` sigue reflejando la realidad?
- ¿Hay deuda técnica que ya vale la pena revisar?
- ¿Las features cerradas cumplen la Definition of Done?
- ¿Alguna decisión irreversible se tomó sin confirmación? (no debería haber pasado)
- ¿El perfil (P3) sigue siendo el correcto?
- ¿Falló algo este ciclo que ninguna regla previó?

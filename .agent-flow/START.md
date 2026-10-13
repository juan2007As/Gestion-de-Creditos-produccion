# Continuidad secuencial entre agentes

Codex y Claude Code usan este protocolo para continuar tareas desde archivos persistentes. Ninguno es principal ni existe una asignación fija de tareas por modelo.

## Al iniciar o retomar

1. Leer el encargo humano, `AGENTS.md` o `CLAUDE.md`, `reglas/00-CORE.md`, `reglas/01-DISPARADORES.md`, `CONTEXTO.md`, `DEUDA-TECNICA.md`, este archivo, `PROJECT.md`, `STATE.md`, `HANDOFF.md` y los conflictos relevantes.
2. Leer las reglas y el código del área afectada, según indique `PROJECT.md`.
3. Confirmar el proyecto, el alcance autorizado y el estado real de Git. Distinguir cambios preexistentes de los de la tarea; nunca descartarlos.
4. Antes de editar, comprobar `STATE.md`. Si figura otro editor, permanecer en lectura. Si figura `ninguno`, solicitar o aplicar la confirmación humana del editor inicial.

Las reglas P3, las paradas por dinero, datos personales, producción, cambios irreversibles y cambio de alcance conservan prioridad. Declararse editor no autoriza desplegar, manejar secretos, modificar datos reales, hacer commits o ampliar el alcance.

## Durante, pausa y relevo

- Mantener `STATE.md` y `HANDOFF.md` actualizados después de avances relevantes y antes de operaciones largas.
- Registrar en `HISTORY.md` avances, pausas, transferencias e intentos fallidos de forma breve. No guardar secretos, transcripciones ni logs completos.
- Tras dos fallos de la misma estrategia, detenerla. Cambiar de agente no reinicia el contador; continuar exige evidencia nueva o decisión humana.
- Para transferir: el editor saliente actualiza el relevo, deja `Editor activo: ninguno` y detiene cambios; la usuaria confirma el entrante; este comprueba archivos reales y se declara editor.
- Si un agente se queda sin cuota o se cierra, el entrante comienza en lectura, inspecciona cambios y procesos antes de repetirlos, y espera confirmación humana de que el anterior dejó de editar.

Una tarea solo termina cuando cumple el alcance y verificaciones autorizados. Registrar lo no verificado y lo fuera de alcance.

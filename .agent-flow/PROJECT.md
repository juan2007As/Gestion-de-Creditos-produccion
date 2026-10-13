# Adaptación del proyecto — Gestión de Créditos

- Proyecto: sistema Django de gestión de créditos.
- Perfil: P3; maneja dinero real y datos personales.
- Continuidad: `.agent-flow/HANDOFF.md` es el relevo operativo canónico porque no existe un `HANDOFF.md` de raíz al instalar este protocolo.
- Instalación inicial: sin tarea real ni editor activo.

## Fuentes de verdad

| Fuente | Uso |
|---|---|
| `AGENTS.md` / `CLAUDE.md` | Instrucciones principales y límites P3. |
| `reglas/00-CORE.md` / `reglas/01-DISPARADORES.md` | Reglas y disparadores aplicables. |
| `CONTEXTO.md` | Decisiones y perfil del proyecto. |
| `DEUDA-TECNICA.md` | Estado técnico conocido. |
| Reglas del área, código y pruebas afectados | Contexto específico de cada tarea. |

## Restricciones

- No ejecutar acciones de producción, dinero, datos personales reales, secretos, borrados o cambios irreversibles sin aprobación humana explícita.
- Comprobar ambiente, datos y respaldo cuando una regla existente lo exija.
- Los comandos de verificación se eligen según la tarea y las reglas existentes; ejecutarlos no autoriza despliegues ni migraciones.

No registrar secretos, tokens, datos personales ni salidas sensibles en `.agent-flow/`.

# Reglas de Git / Control de Versiones (Gestión de Créditos)

> Mantenedor único (el dueño) confirmado en `CONTEXTO.md`. Varias reglas de colaboración de la plantilla madre se aceptan como cajón 4 con su sustituto — ver abajo.

## Principios no negociables

1. Commits pequeños y con un propósito claro cada uno.
2. Mensajes de commit explican el porqué, no solo el qué.
3. Nunca commitear secretos ni `.env` — el escaneo automático (`detect-secrets`, ver [[config-rules]]) ya corre en pre-commit y en CI desde la Fase A4.
4. Nunca usar comandos destructivos (`push --force`, `reset --hard`, `clean -f`) sobre `main` sin confirmar explícitamente con el dueño.
5. Antes de cualquier operación que pueda descartar trabajo, revisar `git status` y guardar/commitear lo pendiente.

## Ramas

6. `main` siempre en estado funcional.
7. Ramas descriptivas (`fix/...`, `feature/...`), no genéricas.
8. Una rama se elimina solo tras confirmar que su trabajo ya está integrado o descartado explícitamente. **Nota real**: existe `origin/fix/production-readiness-17236091267996910219`, de otra sesión de asistente de IA, nunca mergeada, que borra `render.yaml`/`build.sh` completos — pendiente de que el dueño decida si se revisa o se borra (`DEUDA-TECNICA.md` cajón 2 #16).
9. **[P1]** La rama principal está protegida cuando el pipeline lo permita — hoy `render.yaml` tiene `autoDeploy: true` desconectado del resultado del CI (ver [[release-rules]]).

## Secretos y el historial

10. El escaneo de secretos es automático desde la Fase A4 (`.pre-commit-config.yaml` + job `secrets-scan` en `.github/workflows/tests.yml`).
11. **El historial de Git es permanente.** Caso real y actual: la API key de Comfama en `lambda/` sigue visible en el historial de `origin/main` aunque el archivo ya se retiró de la copia de trabajo — sigue comprometida hasta que se rote con Comfama.
12. Ante un secreto filtrado: **revocar primero** (avisar al proveedor externo), desplegar el nuevo, auditar su uso, y solo al final considerar limpiar el historial (operación de force-push, requiere aprobación explícita separada — ver [[config-rules]] §2).
13. `.gitignore` ya cubre `.env`, `db.sqlite3`, `/staticfiles`, `/media` desde antes de esta adopción.

## Revisión de código

14. **Mantenedor único: el sustituto de la revisión por otra persona es releer el diff completo antes de mergear o pushear.** Aceptado como cajón 4 en `DEUDA-TECNICA.md`, no como regla incumplida.
15. Esa relectura mira, como mínimo: ¿hace lo que dice?, ¿rompe algo más ([[integrity-rules]])?, ¿abre algún hueco de autorización?, ¿tiene los tests que le tocan?, ¿deja `CONTEXTO.md`/`DEUDA-TECNICA.md` al día?
16. El diff se revisa entero antes de commitear, incluyendo lo que se coló sin querer.

## Antes de cualquier commit

- ¿Qué archivos se están incluyendo realmente?
- ¿Hay algo que no debería subirse?
- ¿El mensaje explica el porqué?
- ¿Leí el diff completo?
- ¿Este commit deja el proyecto en estado funcional?

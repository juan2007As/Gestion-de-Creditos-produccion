# Reglas de Git / Control de Versiones

## Principios no negociables

1. Commits pequeños y con un propósito claro cada uno — no mezclar un fix con una feature con un refactor en el mismo commit.
2. Mensajes de commit explican el **porqué**, no solo el qué (el diff ya muestra el qué).
3. Nunca commitear secretos, `.env`, ni credenciales — verificar antes de cada commit si hay algo sospechoso, incluso en archivos con nombre inocente.
4. Nunca usar comandos destructivos (`push --force` a ramas compartidas, `reset --hard`, `clean -f`) sin confirmar explícitamente con el usuario primero.
5. Antes de cualquier operación que pueda descartar trabajo (`checkout`, `reset`, `clean`), revisar `git status` y guardar/commitear lo que haya pendiente.

## Ramas

6. La rama principal (`main`/`master`) siempre debe quedar en estado funcional — no se commitea directo ahí trabajo a medias en proyectos con colaboración.
7. Ramas de feature/fix se nombran de forma descriptiva (`feature/login-google`, `fix/overflow-user-card`), no genérico (`fix1`, `test`).
8. Una rama se elimina solo tras confirmar que su trabajo ya está integrado (mergeado) o que el usuario decidió descartarla explícitamente.
9. **[P1]** La rama principal está **protegida**: no se fuerza el historial, no se mergea sin el pipeline en verde, y los cambios entran por el mismo camino para todo el mundo. Ver [[release-rules]].
10. **[P1]** Las ramas de larga duración se sincronizan con la principal con frecuencia. Una rama de tres semanas no se mergea: se negocia.

## Secretos y el historial

11. **[P1]** El escaneo de secretos es **automático**, en pre-commit y en el pipeline. La revisión a ojo antes de commitear falla exactamente el día que hay prisa ([[config-rules]] §2 Secretos).
12. **El historial de Git es permanente.** Un secreto commiteado se considera comprometido aunque el commit se borre después: pudo clonarse, quedar en un fork, en la caché del proveedor o en el portátil de alguien.
13. Si un secreto llega al repositorio, el orden es el de [[config-rules]] §2 Secretos: **revocar primero**, desplegar el nuevo, auditar su uso, y solo al final limpiar el historial. Reescribir la historia sin revocar es dedicar horas a esconder una llave que sigue funcionando.
14. `.gitignore` cubre desde el primer commit: `.env`, credenciales, builds, dependencias instaladas, archivos temporales y volcados de base de datos.

## Revisión de código

15. **[P1]** Está definido qué cambios requieren revisión de otra persona. En proyectos de una sola persona el sustituto es releer el diff completo antes de mergear — el pipeline no detecta un error de lógica de negocio ni un permiso abierto de más.
16. **[P1]** La revisión mira, como mínimo: ¿hace lo que dice?, ¿rompe algo más ([[integrity-rules]])?, ¿abre algún hueco de seguridad o de autorización?, ¿tiene los tests que le tocan?, ¿deja el contexto y las reglas actualizados?
17. **[P1]** El diff se revisa entero antes de commitear, incluyendo lo que se coló sin querer: archivos de configuración del editor, código de depuración, `console.log`, credenciales de prueba, y cambios generados automáticamente que nadie ha leído.

## Antes de cualquier commit

- ¿Qué archivos se están incluyendo realmente? (revisar, no asumir tras un `add` amplio)
- ¿Hay algo que no debería subirse (secretos, archivos temporales, builds)?
- ¿El mensaje explica el porqué del cambio?
- ¿He leído el diff completo, o estoy commiteando cosas que no he mirado?
- ¿Este commit deja el proyecto en un estado funcional?

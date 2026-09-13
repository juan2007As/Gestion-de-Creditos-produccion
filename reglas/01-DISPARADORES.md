# Disparadores — Qué leer según lo que vas a hacer (Gestión de Créditos)

> Se consulta **antes de empezar cualquier tarea**, no después.

## Específico de este proyecto

| Vas a… | Abre | La pregunta que casi siempre se olvida |
|---|---|---|
| **Tocar cálculo de cuotas, mora o interés** (`Cuota`, `CuotaRapida`, `Prestamo`, `PrestamoRapido`) | [[data-rules]] §2 · `DEUDA-TECNICA.md` cajón 1 #1 | ¿Estoy usando `Decimal` en todo el camino, o se cuela un `float()` como en `total_a_pagar()`? ¿Toqué el flujo normal y el de "rápidos" a la vez, o solo uno (y quedaron divergentes otra vez)? |
| **Tocar cualquier vista de pago** (`registrar_pago*`, `pagar_cuota_especifica`) | [[data-rules]] §3 Concurrencia · `mi_app/utilities/transaction_integrity.py` | ¿Esto pasa por `@atomic_payment_view`/`registrar_pago_atomico`, o mueve saldos sin lock como `pagar_cuota_especifica` hoy? |
| **Tocar `mi_app/views_core.py`** | [[integrity-rules]] | Es un archivo de 6000+ líneas: ¿qué más importa esta función? Buscar con grep, no de memoria. |
| **Tocar "préstamos rápidos" (`PrestamoRapido`/`CuotaRapida`/`PagoPrestamoRapido`)** | `DEUDA-TECNICA.md` cajón 2 (duplicación con `Prestamo`/`Cuota`) | ¿Este cambio también aplica al flujo normal? Son ~95% el mismo modelo copy-pasteado — ya divergieron una vez y causó un bug de dinero real. |
| **Tocar login, roles o permisos** (`decorators.py`, `Rol`/`Permiso`/`UsuarioProfile`) | [[identity-rules]] | Recordar: este proyecto **no** aísla por operario a propósito (decisión de negocio). No reintroducir un chequeo de "propiedad de cliente" sin que el dueño lo pida de nuevo. |
| **Agregar o cambiar una variable de entorno en `settings.py`** | [[config-rules]] | ¿Tiene default seguro para dev, y falla el arranque en producción si falta? ¿Está en `.env.example`? |
| **Tocar `build.sh` o `render.yaml`** | [[release-rules]] · [[environments-rules]] | ¿Esto corre en el build o en el arranque? Recordar que `migrate` en el build puede fallar silenciosamente si la DB no está lista todavía. |
| **Instalar o actualizar una dependencia** | [[dependencies-rules]] | `requirements.txt` está con TODAS las versiones fijadas desde la Fase A4 — ¿estoy rompiendo eso al agregar algo sin versión? |
| **Tocar el sistema de backup o `auto_mantenimiento.py`** | [[operations-rules]] · `.github/workflows/backup.yml` | ¿Sigue restaurando de verdad, o solo generando el dump? El workflow falla si no restaura — no lo silencies. |
| **Agregar un dato nuevo de un cliente** | [[compliance-rules]] | ¿De verdad hace falta guardarlo? No hay política de retención definida todavía — ver `DEUDA-TECNICA.md` cajón 2. |
| **Hacer commit** | [[git-rules]] | El hook de `detect-secrets` ya corre — si bloquea, es un falso positivo real o un secreto real, nunca se saltea con `--no-verify` sin mirar cuál de los dos es. |

## Construir

| Vas a… | Abre | La pregunta que casi siempre se olvida |
|---|---|---|
| **Crear o cambiar un endpoint** | [[identity-rules]] §Autorización | ¿Comprobé rol/permiso, o solo que hay sesión? |
| **Devolver una lista de cosas** | [[data-rules]] §6 Rendimiento | `lista_clientes_api` ya devuelve TODO sin paginar (`DEUDA-TECNICA.md` cajón 3) — ¿estoy por repetir el patrón? |
| **Escribir lógica de negocio no trivial** | — | ¿Existe un test que **falle** si esto se rompe? `obtener_profile()`, `calcular_fechas_pago` y `determinar_estado_cuota_al_crear` no tenían ninguno — no sumar una cuarta función así. |

## Datos

| Vas a… | Abre | La pregunta que casi siempre se olvida |
|---|---|---|
| **Añadir o cambiar un campo / una tabla** | [[data-rules]] §1 · §4 Migraciones | Solo hay 2 migraciones para 17 modelos — historial ya reseteado una vez; no asumir que el estado de la BD de Render coincide sin comprobarlo. |
| **Tocar contadores, saldos o montos pendientes** | [[data-rules]] §3 Concurrencia | ¿Qué pasa si dos peticiones hacen esto exactamente a la vez? |
| **Borrar un Cliente (o permitirlo)** | [[data-rules]] §1 · §8 | Hoy es `CASCADE` total hacia `Prestamo`/`Cuota`/`Pago` — borra todo el historial financiero sin avisar. |
| **Escribir un script que modifique datos de producción** | [[data-rules]] §7 | Primero como `SELECT`. Nunca sin `WHERE`. Backup verificado antes (`backup.yml` corrió y restauró hoy). |

## Configuración, dependencias y despliegue

| Vas a… | Abre | La pregunta que casi siempre se olvida |
|---|---|---|
| **Manejar un secreto o credencial** | [[config-rules]] · [[security-rules]] | ¿Puede acabar en un log, una URL o el bundle del frontend? Ya pasó una vez con la key de Comfama. |
| **Desplegar** | [[release-rules]] · [[environments-rules]] | `autoDeploy: true` en Render **no** espera al pipeline todavía — el CI puede estar en rojo y Render despliega igual. |
| **Trabajar en local contra datos reales** | [[environments-rules]] | `EMAIL_BACKEND` es de consola fuera de producción — confirmar que sigue así antes de tocar esa parte. |

## Situaciones (no cambios de código)

| Estás en… | Abre | Lo primero |
|---|---|---|
| **Algo está roto en producción ahora mismo** | [[operations-rules]] | Mitigar primero, entender después. Anotar lo que se toca. |
| **Se filtró un secreto** | [[config-rules]] | Revocar primero (avisar al proveedor externo si aplica, como con Comfama). Limpiar el historial de git es lo último. |
| **Persigues un bug** | [[00-CORE]] §18 | Antes del arreglo, el test que reproduce el fallo — y que se comprueba que falla primero. |
| **Hay prisa y no da tiempo a todo** | [[evolution-rules]] §5 | Se negocia el plazo, no la seguridad ni el rastro. |
| **Entras a este proyecto en una sesión nueva y no tenés todo el contexto** | `CONTEXTO.md` + `DEUDA-TECNICA.md` | Leerlos enteros antes de proponer nada — ya hay una auditoría completa hecha, no repetirla de cero. |

---

## Si nada de la tabla encaja

Entonces el cambio probablemente sea local y trivial, y basta con [[00-CORE]]. Pero antes: **¿toca dinero, datos de un cliente, o producción?** Si la respuesta es sí, no era trivial.

Y si aparece un tipo de tarea recurrente que no está acá, se añade la fila.

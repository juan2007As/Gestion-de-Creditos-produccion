# PASO 13: Reportes

Pruebas en la web para reportes y exportación.

---

## Cómo testear en la web

### 1. Entrar a Reportes
- En el menú superior: **Reportes** (desplegable).
- O desde Inicio: **http://127.0.0.1:8000/** → sección "Reportes".

**Comprobar:** Ves opciones como Estadísticas, Clientes, Préstamos, Cuotas Vencidas, etc.

---

### 2. Reporte de Estadísticas
- Clic en **Estadísticas** (o **Reporte de Estadísticas**).
- URL: `http://127.0.0.1:8000/reportes/estadisticas/`

**Comprobar:**
- La página carga sin error.
- Aparecen métricas (clientes, préstamos, dinero, cuotas, mora, rating, etc.).
- No hay pantalla en blanco ni error 500.

---

### 3. Reporte de Clientes
- Menú Reportes → **Clientes**.
- URL: `http://127.0.0.1:8000/reportes/clientes/`

**Comprobar:**
- Lista/tabla de clientes (incluido Juan Carlos Pérez si lo tienes).
- Filtros o búsqueda si los hay.
- Rating/etiqueta visible si el reporte lo muestra.

---

### 4. Cuotas Vencidas (morosidad)
- Menú Reportes → **Cuotas Vencidas**.
- URL: `http://127.0.0.1:8000/reportes/cuotas-vencidas/`

**Comprobar:**
- La página carga.
- Si hay cuotas vencidas, se listan con cliente, préstamo, días de atraso, mora.
- Si no hay vencidas, mensaje tipo "No hay cuotas vencidas" o tabla vacía.

---

### 5. Exportar a Excel (al menos uno)
- En **cualquier** reporte que tenga botón **Exportar** / **Descargar Excel**.
- O: **Centro de Exportaciones** → `http://127.0.0.1:8000/exportaciones/` → elegir un reporte y exportar.

**Comprobar:**
- Se descarga un archivo `.xlsx`.
- El Excel abre sin error y los datos se ven coherentes con lo que viste en la web.

---

### 6. Histórico de Pagos (opcional)
- Menú Reportes → **Histórico de Pagos**.
- URL: `http://127.0.0.1:8000/reportes/historico-pagos/`

**Comprobar:**
- Lista de pagos (fecha, cliente, monto, etc.).
- Los pagos que registraste (ej. Juan Carlos Pérez) aparecen.

---

## Resumen rápido

| Acción                    | Qué revisar                          |
|---------------------------|--------------------------------------|
| Abrir menú Reportes       | Opciones visibles y enlaces correctos |
| Estadísticas              | Página carga, métricas visibles      |
| Reporte Clientes          | Lista de clientes correcta            |
| Cuotas Vencidas           | Lista de mora o mensaje “sin vencidas” |
| Exportar a Excel          | Descarga .xlsx y abre bien            |
| Histórico de Pagos (opc.) | Pagos registrados aparecen           |

Si algo no carga, da error o no coincide con lo esperado, dime **qué reporte** y **qué viste** (o pega el mensaje de error) y lo revisamos.

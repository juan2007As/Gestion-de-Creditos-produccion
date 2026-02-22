# ✅ PASO 12 – Validación final y scoring

Sigue este checklist para completar la Prueba 12.

---

## 12.A Estado de scoring (en la web)

1. **Entra al perfil del cliente de prueba**
   - URL: `http://127.0.0.1:8000/clientes/` → clic en el cliente (ej. Juan Carlos Pérez, cédula 1234567890)
   - O: `http://127.0.0.1:8000/perfil/<ID_CLIENTE>/`

2. **Revisa la sección "Análisis y Scoring"**
   - Debe aparecer una tarjeta con:
     - **Etiqueta:** BUENO / MEDIO / MALO / SIN_HISTORIAL
     - **Tasa de Cumplimiento:** % (0–100)
     - **Días mora promedio:** número
     - **Scoring (rating 0–5):** valor sobre 5

3. **Comprueba que el rating en la cabecera coincida**
   - Arriba a la derecha: badge (Excelente / Bueno / Regular / Riesgo) según el rating.

**Marcar:**
- [ ] ✅ Vi la sección Análisis y Scoring
- [ ] ✅ Etiqueta y tasa de cumplimiento se ven correctos
- [ ] ✅ El rating (estrellas) coincide con el scoring

---

## 12.B Test de consistencia de datos (script)

Desde la **raíz del proyecto** (`proyecto_john`):

```bash
python pruebas_humano/scripts/verificar_paso12_consistencia.py
```

Si el cliente de prueba tiene cédula `1234567890`, el script comprobará:
- Total prestado (campo vs. suma real)
- Total pagado (modelo vs. suma de pagos en BD)
- Estados de cuotas válidos
- Porcentaje pagado coherente

**Marcar:**
- [ ] ✅ El script terminó con "TODAS LAS VERIFICACIONES PASARON"

Si el script dice que no existe el cliente, crea uno con la guía (Juan Carlos Pérez, 1234567890) o edita `CEDULA_PRUEBA` dentro del script.

---

## 12.C Checklist transversal (opcional)

En `GUIA_TESTING_COMPLETA.md` (Paso 12.1) tienes el checklist largo (Login, Clientes, Préstamos, Cuotas, Pagos, Mora, Reportes, etc.). Puedes ir marcando mentalmente o en papel lo que ya probaste en pasos anteriores.

---

## Resumen Paso 12

Cuando termines:

- **Scoring visible** en perfil del cliente (sección Análisis y Scoring + rating en cabecera).
- **Script de consistencia** ejecutado y en verde.

Si algo falla, anota:
- Qué pantalla estabas viendo
- Qué esperabas
- Qué viste (o el mensaje de error del script).

Con eso se puede revisar y corregir.

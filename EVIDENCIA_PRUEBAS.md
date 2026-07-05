# Evidencia de Pruebas

Se prepararon **dos archivos de prueba** para validar el analizador de logs:
uno bien formado y otro con errores e inconsistencias deliberadas.

---

## Prueba 1 — Archivo bien formado: `logs_validos.txt`

Contiene 10 líneas, todas con severidad válida, mensaje y fecha correcta
`AAAA-MM-DD`.

### Resultado esperado
- Total de eventos válidos: **10**
- INFO: 4 · WARNING: 3 · ERROR: 3
- Todos con fecha válida (10)
- Líneas mal formateadas: 0

### Resultado obtenido (salida real del programa)

```
============================================================
  RESUMEN DEL ANÁLISIS DE: logs_validos.txt
============================================================
  Líneas procesadas (sin contar vacías) : 10
  Líneas en blanco ignoradas            : 0
------------------------------------------------------------
  Total de EVENTOS válidos              : 10
  Eventos por tipo de severidad:
       - INFO    : 4
       - WARNING : 3
       - ERROR   : 3
------------------------------------------------------------
  Eventos CON fecha válida              : 10
  Eventos SIN fecha válida              : 0
  Líneas mal formateadas / incompletas  : 0
============================================================
```

✅ **Coincide con lo esperado.**

---

## Prueba 2 — Archivo con errores: `logs_con_errores.txt`

Contiene casos borde diseñados a propósito:

| Línea | Contenido | Qué prueba | Clasificación esperada |
|------:|-----------|------------|------------------------|
| 1 | `[INFO] 2025-01-10 User logged in` | Caso normal | Válido, con fecha |
| 2 | `[WARNING] Invalid password attempt` | Sin fecha | Válido, sin fecha |
| 3 | `[error] 2025-01-11 ...` | Severidad en minúscula | Válido, con fecha |
| 4 | `[ERROR] 2025-13-45 ...` | **Fecha imposible** | Válido, sin fecha válida |
| 5 | `[INFO]` | Severidad sin mensaje | Mal formateada |
| 6 | `Este renglon no tiene nivel...` | Sin severidad | Mal formateada |
| 7 | `[ERROR] 2025-01-11 ...` | Caso normal | Válido, con fecha |
| 8 | *(línea en blanco)* | Vacía | Ignorada |
| 9 | `[warning] 2025/01/12 ...` | Fecha con barras | Válido, sin fecha válida |
| 10 | `[INFO] 2025-1-9 ...` | Fecha sin ceros | Válido, sin fecha válida |
| 11 | `[CRITICAL] 2025-01-15 ...` | Nivel no soportado | Mal formateada |
| 12 | `· [INFO] 2025-01-16 ...` | Punto decorativo inicial | Válido, con fecha |
| 13 | `[WARNING]` | Severidad sin mensaje | Mal formateada |

### Resultado esperado
- Total de eventos válidos: **8** (INFO: 3 · WARNING: 2 · ERROR: 3)
- Con fecha válida: 4 · Sin fecha válida: 4
- Líneas mal formateadas: 4 (líneas 5, 6, 11, 13)
- Líneas en blanco ignoradas: 1 (línea 8)

### Resultado obtenido (salida real del programa)

```
============================================================
  RESUMEN DEL ANÁLISIS DE: logs_con_errores.txt
============================================================
  Líneas procesadas (sin contar vacías) : 12
  Líneas en blanco ignoradas            : 1
------------------------------------------------------------
  Total de EVENTOS válidos              : 8
  Eventos por tipo de severidad:
       - INFO    : 3
       - WARNING : 2
       - ERROR   : 3
------------------------------------------------------------
  Eventos CON fecha válida              : 4
  Eventos SIN fecha válida              : 4
  Líneas mal formateadas / incompletas  : 4
============================================================

  DETALLE DE LÍNEAS MAL FORMATEADAS:
    Línea   5: Tiene severidad pero no contiene mensaje
    Línea   6: Sin nivel de severidad reconocible ([INFO]/[WARNING]/[ERROR])
    Línea  11: Sin nivel de severidad reconocible ([INFO]/[WARNING]/[ERROR])
    Línea  13: Tiene severidad pero no contiene mensaje
============================================================
```

✅ **Coincide exactamente con lo esperado.** El programa distingue correctamente
entre fechas reales y fechas con formato inválido o imposible, reconoce la severidad
sin importar mayúsculas/minúsculas, tolera el punto decorativo inicial, y separa las
líneas mal formateadas de los eventos válidos indicando el motivo de cada una.

---

## Cómo reproducir las pruebas

```bash
python analizador_logs.py logs_validos.txt
python analizador_logs.py logs_con_errores.txt
```

También se puede ejecutar sin argumentos y el programa pedirá la ruta del archivo:

```bash
python analizador_logs.py
```

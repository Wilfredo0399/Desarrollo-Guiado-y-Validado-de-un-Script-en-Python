# Desarrollo Guiado y Validado de un Script en Python

Analizador de archivos de **log / registros de eventos** desarrollado en Python,
usando la IA como herramienta de apoyo pero manteniendo bajo control humano las
reglas de validación y las decisiones de diseño.

## ¿Qué hace?

Lee un archivo de texto donde cada línea es un evento y:

- Identifica el **nivel de severidad**: `INFO`, `WARNING` o `ERROR`.
- Detecta si la línea tiene o no una **fecha válida** (`AAAA-MM-DD` que exista
  de verdad en el calendario).
- Genera un **resumen** con: total de eventos, cantidad por tipo, eventos con y sin
  fecha, y número de líneas mal formateadas o incompletas (con el detalle de cada una).
- Muestra todo de forma clara en consola.

## Requisitos

- Python 3.8 o superior (probado en Python 3.13). No requiere librerías externas.

## Uso

```bash
# Pasando el archivo como argumento
python analizador_logs.py logs_validos.txt

# O sin argumentos: el programa pedirá la ruta del archivo
python analizador_logs.py
```

## Contenido del repositorio

| Archivo | Descripción |
|---------|-------------|
| `analizador_logs.py` | Script principal (funcional y comentado). |
| `logs_validos.txt` | Archivo de prueba bien formado. |
| `logs_con_errores.txt` | Archivo de prueba con errores y casos borde. |
| `REFLEXION_TECNICA.md` | Documento de reflexión técnica sobre el uso de IA. |
| `EVIDENCIA_PRUEBAS.md` | Evidencia de pruebas: resultados esperados vs obtenidos. |

## Reglas de validación (decisiones del desarrollador)

- Una línea es un **evento válido** si empieza con `[INFO]`, `[WARNING]` o `[ERROR]`
  y contiene un mensaje.
- La **fecha es opcional**: una línea sin fecha (o con fecha mal escrita) sigue siendo
  un evento válido; solo se reporta que no tiene fecha válida.
- Las líneas **sin severidad** o **sin mensaje** se cuentan como *mal formateadas*
  (no se ignoran en silencio ni se confunden con errores de la aplicación).
- Las líneas en blanco se ignoran.

Estas reglas están explicadas con más detalle en `REFLEXION_TECNICA.md` y comentadas
dentro del propio código.

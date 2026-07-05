# Documento de Reflexión Técnica

**Actividad:** Desarrollo guiado y validado de un script en Python
**Tema:** Analizador de archivos de log / registros de eventos
**Autor:** Wilfredo

---

## 1. Qué partes fueron apoyadas por IA y cuáles fueron decisión propia

### Apoyado / sugerido por la IA
- **Expresiones regulares.** Le pedí a la IA una propuesta de expresión regular
  para detectar la severidad al inicio de la línea y otra para detectar fechas en
  formato `AAAA-MM-DD`. Partí de esas propuestas.
- **Estructura general de funciones.** La idea de separar el trabajo en funciones
  (`analizar_linea`, `analizar_archivo`, `mostrar_resumen`) surgió como sugerencia
  de organización del código.
- **Detalles idiomáticos de Python.** Uso de `collections.Counter` para contar por
  nivel y el `try/except` con `datetime.strptime` para validar fechas.
- **Explicaciones puntuales.** Le pregunté para qué sirve `sys.stdout.reconfigure`
  y por qué en Windows los acentos se ven mal en consola.

### Decisiones que tomé yo (no delegadas a la IA)
La guía es clara en que **las reglas de validación no las debe definir la IA**.
Estas decisiones las tomé y las dejé documentadas dentro del propio código:

1. **Qué es una línea válida:** debe empezar con `[INFO]`, `[WARNING]` o `[ERROR]`.
   Esa es la información mínima de un evento.
2. **Qué cuenta como línea mal formateada:** las que no tienen severidad
   reconocible **o** las que tienen severidad pero se quedan sin mensaje.
3. **La fecha es opcional:** decidí que una línea sin fecha (o con fecha mal escrita)
   **sigue siendo un evento válido**; solo se marca que no tiene fecha válida. No la
   descarto ni la cuento como error.
4. **Cómo tratar las líneas mal formateadas:** contarlas aparte y mostrarlas en un
   detalle, en lugar de ignorarlas en silencio o mezclarlas con los `ERROR`.
5. **Casos borde que sí manejo:** líneas en blanco (se ignoran), severidad en
   minúsculas (`[error]`), punto/guion decorativo al inicio (`· [INFO] ...`),
   fechas imposibles como `2025-13-45`, y formatos de fecha no aceptados
   (`2025/01/12`, `2025-1-9`).
6. **Casos borde que decidí NO manejar:** no intento "adivinar" ni corregir fechas
   mal escritas, ni soporto otros formatos de fecha distintos a `AAAA-MM-DD`, ni
   niveles de severidad fuera de los tres pedidos (`[CRITICAL]` se trata como línea
   mal formateada a propósito).

---

## 2. Ejemplo concreto: la IA sugirió algo mejorable y lo corregí

**Sugerencia inicial de la IA (validación de fecha solo con regex):**

```python
# Propuesta de la IA: dar por válida la fecha si "tiene la forma" AAAA-MM-DD
PATRON_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")

def tiene_fecha_valida(texto):
    return bool(PATRON_FECHA.search(texto))
```

**Problema que detecté:** esta versión acepta como válida una fecha imposible como
`2025-13-45` (mes 13, día 45), porque la expresión regular solo comprueba la
**forma** (cuatro dígitos, guion, dos dígitos, guion, dos dígitos), no que la fecha
**exista** en el calendario. Para un analizador de logs eso es un falso positivo:
estaría reportando como "fecha válida" algo que no lo es.

**Mi corrección:** la expresión regular solo propone un candidato; después valido
que sea un día real convirtiéndolo con `datetime`:

```python
def tiene_fecha_valida(texto):
    coincidencia = PATRON_FECHA.search(texto)
    if not coincidencia:
        return False
    try:
        datetime.strptime(coincidencia.group(1), "%Y-%m-%d")
        return True
    except ValueError:
        return False  # la forma era correcta pero el día no existe
```

Lo comprobé con el archivo de prueba `logs_con_errores.txt`, que incluye la línea
`[ERROR] 2025-13-45 Fecha imposible en el calendario`: el programa la clasifica
correctamente como evento **sin fecha válida**, no como fecha buena.

---

## 3. Qué aprendí sobre el uso de la IA como herramienta y no como reemplazo

- La IA es muy útil para **arrancar rápido**: proponer una regex, recordar una función
  de la librería estándar o explicar un bloque de código que no conocía. Me ahorró
  tiempo de búsqueda.
- Pero **no se puede confiar a ciegas**. El ejemplo de la validación de fechas muestra
  que una solución que "parece correcta" puede tener un fallo de criterio (validar la
  forma en vez del valor real). Detectar eso depende de entender **el problema**, no
  solo el código.
- Las **reglas de negocio** (qué es un evento válido, qué hago cuando falta la fecha,
  qué casos borde ignoro) son decisiones que tienen que ser mías, porque son las que
  se califican y de las que soy responsable. La IA no conoce el contexto de la tarea
  mejor que yo.
- Aprendí a usar la IA como un **asistente que propone y explica**, mientras que la
  **validación, las pruebas y las decisiones finales** quedan de mi lado. Probar el
  código con dos archivos reales (uno bien formado y uno con errores) fue lo que me
  dio la confianza de que la solución realmente funciona.

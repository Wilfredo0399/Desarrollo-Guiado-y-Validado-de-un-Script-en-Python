"""
analizador_logs.py
==================

Analizador de archivos de log / registros de eventos.

Cada línea del archivo representa un evento y puede contener:
    - Nivel de severidad: INFO, WARNING o ERROR   (ej. "[INFO]")
    - Marca de tiempo:    fecha AAAA-MM-DD          (puede estar bien o mal formateada)
    - Mensaje:            texto libre

El programa:
    1. Permite al usuario elegir el archivo a analizar.
    2. Clasifica cada línea por severidad e indica si tiene fecha válida.
    3. Genera un resumen: total de eventos, cantidad por tipo y
       número de líneas mal formateadas o incompletas.
    4. Muestra el resultado de forma clara en consola.

--------------------------------------------------------------------------
DECISIONES DE DISEÑO TOMADAS POR EL DESARROLLADOR (no delegadas a la IA)
--------------------------------------------------------------------------
Las reglas de validación son la parte que la guía pide que decida el
estudiante, NO la IA. Aquí quedan documentadas de forma explícita:

  * ¿Qué es una línea VÁLIDA?
        Debe empezar con un nivel de severidad reconocido entre corchetes:
        [INFO], [WARNING] o [ERROR] (sin distinguir mayúsculas/minúsculas).
        Esa es la información mínima imprescindible de un evento.

  * ¿Qué es una línea MAL FORMATEADA / INCOMPLETA?
        - No tiene severidad reconocible al inicio, o
        - La severidad existe pero no queda ningún mensaje después de ella.
        Estas líneas se CUENTAN aparte (no se ignoran en silencio) para que
        el resumen sea honesto. Decisión: contarlas como "mal formateadas",
        NO como errores de severidad ERROR, porque son problemas de FORMATO,
        no eventos de la aplicación.

  * ¿Qué pasa con la FECHA?
        Es un dato OPCIONAL. Una línea con severidad y mensaje pero sin fecha
        (o con fecha mal escrita) sigue siendo un evento VÁLIDO; simplemente
        se marca "fecha_valida = False". Decisión: la ausencia de fecha NO
        invalida el evento, solo se reporta.
        Se considera fecha válida únicamente un formato AAAA-MM-DD que además
        sea un día real del calendario (por eso se valida con datetime y no
        solo con la expresión regular).

  * Líneas en blanco: se ignoran por completo (no cuentan para nada).
--------------------------------------------------------------------------
"""

import re
import sys
import os
from collections import Counter
from datetime import datetime

# En Windows la consola suele usar una codificación (cp1252/cp850) que no
# muestra bien los acentos. Forzamos UTF-8 en la salida para que el resumen
# se vea correcto en cualquier terminal. Decisión: hacerlo tolerante a fallos
# (si la consola no lo permite, el programa sigue funcionando igual).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# ---------------------------------------------------------------------------
# Expresiones regulares
# ---------------------------------------------------------------------------
# La severidad debe aparecer entre corchetes al inicio de la línea.
# Se permite un guion o punto decorativo inicial ("· [INFO] ...") como el que
# aparece en los ejemplos de la guía, y espacios sobrantes.
PATRON_SEVERIDAD = re.compile(r"^[\s·\-*]*\[(INFO|WARNING|ERROR)\]\s*(.*)$",
                              re.IGNORECASE)

# La fecha se busca en formato AAAA-MM-DD en cualquier parte del resto de la
# línea. La regex solo valida la FORMA; que sea un día real se comprueba luego
# con datetime (decisión del desarrollador: regex propone, datetime confirma).
PATRON_FECHA = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

# Niveles válidos definidos por el desarrollador.
NIVELES_VALIDOS = ("INFO", "WARNING", "ERROR")


def tiene_fecha_valida(texto):
    """Devuelve True si el texto contiene una fecha AAAA-MM-DD que existe
    de verdad en el calendario (ej. 2025-02-30 NO es válida).

    Decisión: no basta con que 'parezca' fecha; debe poder convertirse con
    datetime, así descartamos fechas imposibles como el 31 de febrero.
    """
    coincidencia = PATRON_FECHA.search(texto)
    if not coincidencia:
        return False
    try:
        datetime.strptime(coincidencia.group(1), "%Y-%m-%d")
        return True
    except ValueError:
        # La forma era correcta pero el día no existe -> no es fecha válida.
        return False


def analizar_linea(linea):
    """Analiza una única línea del log.

    Devuelve un diccionario con el resultado de la clasificación:
        {
            "valida": bool,          # True si es un evento reconocible
            "nivel": str | None,     # INFO / WARNING / ERROR o None
            "fecha_valida": bool,    # si contiene una fecha real
            "mensaje": str,          # texto del evento (sin severidad)
            "motivo": str,           # explicación si la línea es inválida
        }
    """
    texto = linea.strip()

    # Base del resultado.
    resultado = {
        "valida": False,
        "nivel": None,
        "fecha_valida": False,
        "mensaje": "",
        "motivo": "",
    }

    coincidencia = PATRON_SEVERIDAD.match(texto)

    # Caso 1: no hay severidad reconocible -> línea mal formateada.
    if not coincidencia:
        resultado["motivo"] = "Sin nivel de severidad reconocible ([INFO]/[WARNING]/[ERROR])"
        return resultado

    nivel = coincidencia.group(1).upper()   # normalizamos a mayúsculas
    resto = coincidencia.group(2).strip()   # todo lo que sigue a la severidad

    # Caso 2: hay severidad pero no queda mensaje -> línea incompleta.
    if resto == "":
        resultado["nivel"] = nivel
        resultado["motivo"] = "Tiene severidad pero no contiene mensaje"
        return resultado

    # Caso 3: línea válida. Reportamos si además trae fecha real.
    resultado["valida"] = True
    resultado["nivel"] = nivel
    resultado["fecha_valida"] = tiene_fecha_valida(resto)
    resultado["mensaje"] = resto
    return resultado


def analizar_archivo(ruta):
    """Lee el archivo indicado y analiza todas sus líneas.

    Devuelve una tupla (estadisticas, detalles) donde:
        estadisticas -> dict con los totales para el resumen.
        detalles     -> lista con el análisis de cada línea (para el reporte).
    """
    estadisticas = {
        "total_eventos": 0,          # líneas válidas (eventos reconocidos)
        "por_nivel": Counter(),      # conteo por INFO/WARNING/ERROR
        "con_fecha_valida": 0,       # eventos válidos que traen fecha real
        "sin_fecha_valida": 0,       # eventos válidos sin fecha o con fecha mala
        "mal_formateadas": 0,        # líneas inválidas / incompletas
        "lineas_vacias": 0,          # líneas en blanco (ignoradas)
    }
    detalles = []

    # Se usa encoding utf-8 para admitir acentos y símbolos. errors="replace"
    # evita que un byte raro rompa todo el análisis (decisión: ser tolerante
    # a la codificación del archivo de entrada).
    with open(ruta, "r", encoding="utf-8", errors="replace") as archivo:
        for numero, linea in enumerate(archivo, start=1):

            # Las líneas en blanco no aportan información: se ignoran.
            if linea.strip() == "":
                estadisticas["lineas_vacias"] += 1
                continue

            res = analizar_linea(linea)
            res["numero"] = numero
            detalles.append(res)

            if res["valida"]:
                estadisticas["total_eventos"] += 1
                estadisticas["por_nivel"][res["nivel"]] += 1
                if res["fecha_valida"]:
                    estadisticas["con_fecha_valida"] += 1
                else:
                    estadisticas["sin_fecha_valida"] += 1
            else:
                estadisticas["mal_formateadas"] += 1

    return estadisticas, detalles


def mostrar_resumen(estadisticas, detalles, ruta):
    """Imprime el resumen del análisis de forma clara en consola."""
    print("\n" + "=" * 60)
    print(f"  RESUMEN DEL ANÁLISIS DE: {os.path.basename(ruta)}")
    print("=" * 60)

    total_lineas = estadisticas["total_eventos"] + estadisticas["mal_formateadas"]
    print(f"  Líneas procesadas (sin contar vacías) : {total_lineas}")
    print(f"  Líneas en blanco ignoradas            : {estadisticas['lineas_vacias']}")
    print("-" * 60)
    print(f"  Total de EVENTOS válidos              : {estadisticas['total_eventos']}")
    print("  Eventos por tipo de severidad:")
    for nivel in NIVELES_VALIDOS:
        print(f"       - {nivel:<8}: {estadisticas['por_nivel'].get(nivel, 0)}")
    print("-" * 60)
    print(f"  Eventos CON fecha válida              : {estadisticas['con_fecha_valida']}")
    print(f"  Eventos SIN fecha válida              : {estadisticas['sin_fecha_valida']}")
    print(f"  Líneas mal formateadas / incompletas  : {estadisticas['mal_formateadas']}")
    print("=" * 60)

    # Detalle de las líneas problemáticas: útil para depurar el archivo.
    problematicas = [d for d in detalles if not d["valida"]]
    if problematicas:
        print("\n  DETALLE DE LÍNEAS MAL FORMATEADAS:")
        for d in problematicas:
            print(f"    Línea {d['numero']:>3}: {d['motivo']}")
        print("=" * 60)
    print()


def pedir_ruta():
    """Determina qué archivo analizar.

    Prioridad de selección (decisión de diseño):
        1. Si se pasó una ruta como argumento de línea de comandos, se usa esa.
        2. Si no, se pregunta al usuario por consola.
    Repite la pregunta hasta obtener una ruta de archivo existente.
    """
    # Opción 1: argumento en la terminal -> python analizador_logs.py archivo.txt
    if len(sys.argv) > 1:
        return sys.argv[1]

    # Opción 2: preguntar de forma interactiva.
    while True:
        ruta = input("Ingresa la ruta del archivo de log a analizar: ").strip().strip('"')
        if ruta == "":
            print("  >> No escribiste nada. Intenta de nuevo.\n")
            continue
        if not os.path.isfile(ruta):
            print(f"  >> No se encontró el archivo '{ruta}'. Verifica la ruta.\n")
            continue
        return ruta


def main():
    """Punto de entrada del programa."""
    ruta = pedir_ruta()

    # Validación de existencia también cuando la ruta viene por argumento,
    # para dar un mensaje de error claro en lugar de una traza fea.
    if not os.path.isfile(ruta):
        print(f"ERROR: no se encontró el archivo '{ruta}'.")
        sys.exit(1)

    try:
        estadisticas, detalles = analizar_archivo(ruta)
    except PermissionError:
        print(f"ERROR: no hay permisos para leer '{ruta}'.")
        sys.exit(1)
    except OSError as e:
        # Cualquier otro problema de lectura del archivo.
        print(f"ERROR al leer el archivo: {e}")
        sys.exit(1)

    mostrar_resumen(estadisticas, detalles, ruta)


if __name__ == "__main__":
    main()

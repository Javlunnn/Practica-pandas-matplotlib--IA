"""
Práctica de laboratorio: Análisis y visualización de calificaciones con Pandas y Matplotlib
Tópicos Avanzados de Programación - ISC - Instituto Tecnológico de Ciudad Madero

Nombre del estudiante:
Número de control:
Fecha:

Uso:
    python practica_pandas.py      -> ejecuta los seis ejercicios en consola
    python interfaz.py             -> abre la interfaz gráfica

Cada ejercicio es una función, para que la interfaz pueda ejecutarlos por separado.
Los archivos se leen y se guardan en la carpeta donde está este script.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

APROBATORIA = 70
CARPETA = Path(__file__).resolve().parent
ARCHIVO_CSV = CARPETA / "calificaciones_isc.csv"

# Mostrar todas las columnas al imprimir DataFrames
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def cargar_datos():
    """Lee el CSV y devuelve el DataFrame df."""
    return pd.read_csv(ARCHIVO_CSV)


def agregar_situacion(df):
    """Columna situacion sin ciclo: Aprobado si calificacion >= 70."""
    df["situacion"] = np.where(df["calificacion"] >= APROBATORIA, "Aprobado", "Reprobado")
    return df


# ----------------------------------------------------------------------
# Ejercicio 1. Carga y revisión
# ----------------------------------------------------------------------
def ejercicio1(df):
    titulo("Ejercicio 1. Carga y revisión")

    print("Primeras 5 filas:")
    print(df.head())

    filas, columnas = df.shape
    print(f"\nFilas: {filas}   Columnas: {columnas}")

    print("\nTipo de dato de cada columna:")
    print(df.dtypes)

    print("\nResumen estadístico de calificacion y asistencias:")
    print(df[["calificacion", "asistencias"]].describe())

    # ¿Por qué 288 registros y no 24?
    # Cada fila no es un alumno, sino UNA calificación de un alumno en una
    # materia y una unidad. Son 24 alumnos x 4 materias x 3 unidades = 288 filas.
    print("\n288 registros = 24 alumnos x 4 materias x 3 unidades "
          "(cada fila es una unidad evaluada, no un alumno).")


# ----------------------------------------------------------------------
# Ejercicio 2. Filtros (sin modificar df y sin ciclos)
# ----------------------------------------------------------------------
def ejercicio2(df):
    titulo("Ejercicio 2. Filtros")

    grupo_a = df[df["grupo"] == "A"]
    menores_70 = df[df["calificacion"] < APROBATORIA]
    bd_b_80 = df[
        (df["materia"] == "Bases de datos")
        & (df["grupo"] == "B")
        & (df["calificacion"] >= 80)
    ]

    print(f"Filas del grupo A:                               {len(grupo_a)}")
    print(f"Unidades con calificación menor a 70:            {len(menores_70)}")
    print(f"Bases de datos, grupo B, calificación >= 80:     {len(bd_b_80)}")


# ----------------------------------------------------------------------
# Ejercicio 3. Columna calculada (sin ciclo)
# ----------------------------------------------------------------------
def ejercicio3(df):
    titulo("Ejercicio 3. Columna calculada")

    agregar_situacion(df)
    print(df[["matricula", "materia", "unidad", "calificacion", "situacion"]].head(10))


# ----------------------------------------------------------------------
# Ejercicio 4. Resúmenes
# ----------------------------------------------------------------------
def ejercicio4(df):
    titulo("Ejercicio 4. Resúmenes")

    if "situacion" not in df.columns:
        agregar_situacion(df)

    prom_materia = df.groupby("materia")["calificacion"].mean().round(2)
    print("Promedio de calificación por materia:")
    print(prom_materia)

    prom_grupo_materia = df.groupby(["grupo", "materia"])["calificacion"].mean().round(2)
    print("\nPromedio por grupo y materia:")
    print(prom_grupo_materia)

    prom_alumno = (
        df.groupby(["matricula", "nombre"])["calificacion"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )
    print("\nPromedio general por alumno (mayor a menor):")
    print(prom_alumno)

    prom_unidad = df.groupby("unidad")["calificacion"].mean().round(2)
    print("\nPromedio general por unidad (todas las materias):")
    print(prom_unidad)

    conteo_situacion = df["situacion"].value_counts()
    print("\nUnidades aprobadas y reprobadas:")
    print(conteo_situacion)

    # Exportar: reset_index() recupera matricula y nombre como columnas,
    # index=False evita la columna extra 0, 1, 2...
    promedios_alumnos = prom_alumno.reset_index().rename(columns={"calificacion": "promedio"})
    promedios_alumnos.to_csv(CARPETA / "promedios_alumnos.csv", index=False)
    print("\nArchivo creado: promedios_alumnos.csv")


# ----------------------------------------------------------------------
# Ejercicio 5. Gráficas (primero savefig, después show)
# ----------------------------------------------------------------------
def ejercicio5(df, mostrar=True):
    titulo("Ejercicio 5. Gráficas")

    # 5.1 Barras del promedio por materia
    prom_materia = df.groupby("materia")["calificacion"].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    barras = ax.bar(prom_materia.index, prom_materia.values, color="#4C72B0")
    ax.bar_label(barras, fmt="%.1f")
    ax.axhline(APROBATORIA, color="red", linestyle="--", linewidth=1, label="Mínimo aprobatorio (70)")
    ax.set_ylim(0, 100)
    ax.set_title("Promedio de calificación por materia")
    ax.set_xlabel("Materia")
    ax.set_ylabel("Calificación promedio")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CARPETA / "promedio_materias.png", dpi=120)
    print("Archivo creado: promedio_materias.png")

    # 5.2 Histograma de todas las calificaciones
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["calificacion"], bins=range(40, 105, 5), color="#55A868", edgecolor="black")
    ax.axvline(APROBATORIA, color="red", linestyle="--", linewidth=2, label="Calificación 70")
    ax.set_title("Distribución de todas las calificaciones")
    ax.set_xlabel("Calificación")
    ax.set_ylabel("Número de unidades evaluadas")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CARPETA / "histograma.png", dpi=120)
    print("Archivo creado: histograma.png")

    # 5.3 Líneas del promedio por unidad, una por materia
    tendencia = df.groupby(["unidad", "materia"])["calificacion"].mean().unstack()
    fig, ax = plt.subplots(figsize=(8, 5))
    for materia in tendencia.columns:
        ax.plot(tendencia.index, tendencia[materia], marker="o", label=materia)
    ax.axhline(APROBATORIA, color="gray", linestyle=":", linewidth=1)
    ax.set_xticks([1, 2, 3])
    ax.set_title("Tendencia del promedio por unidad y materia")
    ax.set_xlabel("Unidad")
    ax.set_ylabel("Calificación promedio")
    ax.legend(title="Materia")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(CARPETA / "tendencia_unidades.png", dpi=120)
    print("Archivo creado: tendencia_unidades.png")

    print("\nPromedio por unidad y materia (datos de la gráfica de líneas):")
    print(tendencia.round(2))

    if mostrar:
        plt.show()
    plt.close("all")


# ----------------------------------------------------------------------
# Ejercicio 6. Lectura de resultados
# ----------------------------------------------------------------------
INTERPRETACION = """
Interpretación (números tomados de los resúmenes del ejercicio 4 y las gráficas):

1. Materia con el promedio más bajo:
   Bases de datos, con 74.64. Le siguen Programacion (75.50),
   Matematicas discretas (75.75) y Redes (76.67), la más alta. La diferencia
   entre la más baja y la más alta es de apenas 2 puntos. El grupo B supera
   al A en todas las materias; la brecha mayor está en Redes (79.17 contra 74.17).

2. ¿La unidad 3 tiene un promedio menor que las unidades 1 y 2?
   Sí. Unidad 1: 77.07, unidad 2: 78.12, unidad 3: 71.72. La unidad 3 cae
   más de 6 puntos respecto a la unidad 2. La gráfica de tendencia muestra
   que la caída ocurre en las cuatro materias; la más marcada es
   Matematicas discretas, que pasa de casi 81 en la unidad 2 a cerca de 70
   en la unidad 3, justo en el límite aprobatorio.

3. ¿Cuántos alumnos quedan bajo 70 en su promedio general?
   Uno solo: Ana Lopez (ISC240100), con 68.33. El siguiente promedio más
   bajo es Pedro Perez con 71.25. Aun así, 89 de las 288 unidades (31 %)
   salieron reprobadas, contra 199 aprobadas: muchos alumnos reprueban
   unidades sueltas pero lo compensan en el promedio general.
"""


def ejercicio6(df=None):
    titulo("Ejercicio 6. Lectura de resultados")
    print(INTERPRETACION)


def main(mostrar=True):
    df = cargar_datos()
    ejercicio1(df)
    ejercicio2(df)
    ejercicio3(df)
    ejercicio4(df)
    ejercicio5(df, mostrar=mostrar)
    ejercicio6(df)


if __name__ == "__main__":
    main()

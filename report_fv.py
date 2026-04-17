# TAREA 3 — Reporte con pandas (20 pts)
#
# 1. *Carga todos los registros de la tabla `pokemon` a un DataFrame
# 2. Calcula estadísticas descriptivas (mean, std, min, max, mediana)
#    para: stat_hp, stat_ataque, stat_defensa, stat_velocidad
# 3. *Agrega columna: stat_total = suma de los 6 stats
# 4. *Exporta el DataFrame completo a: reporte_pokemon.csv
# 5. *Imprime por consola el top 5 por stat_total
# 6. Crea un csv con summary

import pandas as pd

import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# --------------- PASO 1: de la DB pokedata a DataFrame de Pandas ---------------
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
query = "SELECT * FROM pokemon;"

df = pd.read_sql(query, conn)

conn.close

print("Primeros 6 registros:")
print(df.head(6))
print()

# Información de columnas del dataframe
print("Información del dataframe:")
print(df.info())
print()

# Cambiar tipo de datos columna "poke_id" de int64 a object
df["poke_id"] = df["poke_id"].astype(str)
print("Cambio exitoso del tipo de dato de 'poke_id' de int64 a object:")
print(df.dtypes)
print()


# --------------- PASO 2: cálculo de estadísticas descriptivas ---------------
# Estadísticas descriptivas para columnas numéricas
df_describe = df.describe()
median = df.select_dtypes(include=["number"]).median() # Obtener mediana de columnas numéricas
median.name = "median" # Nombrar la Serie Pandas como "median"
df_describe = pd.concat([df_describe, median.to_frame().T]) # Concatenar con "df_describe"
print("Estadísticas descriptivas para columnas numéricas:")
print(df_describe)
print()

# Estadísticas descriptivas para columnas no numéricas
print("Estadísticas descriptivas para columnas no numéricas:")
print(df.describe(include=['object']))
print()


# --------------- PASO 3: agregar columna "stat_total" ---------------
df["stat_total"] = (df["stat_hp"] 
                    + df["stat_ataque"] 
                    + df["stat_defensa"]
                    + df["stat_velocidad"]
                    + df["stat_ataque_especial"]
                    + df["stat_defensa_especial"]
                   )

print("Mostrar primeros 6 registros con nueva columna 'stat_total")
print(df.head(6))
print()

# --------------- PASO 4: exportar DataFrame completo ---------------
try:
    df.to_csv("reporte_pokemon.csv", index=False)
    print("Reporte pokemon generado exitosamente: reporte_pokemon.csv")
    print()
except Exception as e:
    print(f"Error al generar reporte pokemon (paso 4): {e}")

# --------------- PASO 5: top 5 stat_total en consola ---------------
# Top 5 stat_total en orden descendente
print("Top 5 stat_total en orden descendente:")
top_5 = df.sort_values(by="stat_total", ascending=False).head(5)
print(top_5)
print()

# --------------- PASO 6: generar algunas métricas y crear summary ---------------

# 1. Conteo y porcentaje por tipo primario → distribución de Pokémon por su tipo principal
m1 = (
    df.groupby("tipo_primario")
    .agg(
        conteo=("poke_id", "count"),
        porcentaje=("poke_id", lambda x: len(x) / len(df) * 100)
    )
)

# 2. Conteo y porcentaje por tipo secundario → distribución considerando el segundo tipo (puede haber NaN)
m2 = (
    df.groupby("tipo_secundario")
    .agg(
        conteo=("poke_id", "count"),
        porcentaje=("poke_id", lambda x: len(x) / len(df) * 100)
    )
)

# 3. Estadísticas descriptivas de stat_total → resumen de distribución (media, std, min, max, etc.)
m3 = df["stat_total"].describe()

# 4. Clasificación por nivel → segmenta Pokémon en débil, medio y fuerte según stat_total
df["nivel"] = pd.cut(
    df["stat_total"],
    bins=[0, 300, 400, 1000],
    labels=["débil", "medio", "fuerte"]
)

m4 = df["nivel"].value_counts()

# 5. Mejor Pokémon por tipo primario → obtiene el de mayor stat_total en cada tipo
m5 = df.loc[df.groupby("tipo_primario")["stat_total"].idxmax()]

# 6. Correlación con stat_total → mide qué stats están más relacionados con el poder total
m6 = df.corr(numeric_only=True)["stat_total"].sort_values(ascending=False)


# Crear carpeta "summary" si no existe
import os
os.makedirs("summary", exist_ok=True)

# Guardar csv archivos dentro
try:
    m1.to_csv("summary/tipo_primario.csv")
    m2.to_csv("summary/tipo_secundario.csv")
    m3.to_csv("summary/stat_total_describe.csv")
    m4.to_csv("summary/niveles.csv")
    m5.to_csv("summary/top_por_tipo.csv", index=False)
    m6.to_csv("summary/correlaciones.csv")
    print("Summary generado exitosamente: seis csv en total dentro de la carpeta.")
    print()
except Exception as e:
    print(f"Error en la creación del summary: {e}")
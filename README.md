# pokemon-etl-project

## 📌 Descripción
Pipeline ETL en Python que consume datos de PokéAPI, los transforma y los almacena en una base de datos PostgreSQL. Se realiza un análisis exploratorio con pandas, generando métricas descriptivas, segmentaciones y rankings de Pokémon basados en sus estadísticas. Finalmente, se exportan reportes en formato CSV para facilitar su consulta y análisis.

---

## ⚙️ Flujo del proyecto

1. **Ingesta de datos (ETL)**
   - Consumo de la PokéAPI
   - Extracción de información de Pokémon
   - Transformación de datos (stats, tipos, atributos físicos)
   - Carga en base de datos PostgreSQL

2. **Análisis de datos**
   - Lectura de datos desde PostgreSQL
   - Cálculo de estadísticas descriptivas
   - Creación de variable `stat_total`
   - Segmentación por niveles de poder según `stat_total`
   - Análisis por tipo de Pokémon
   - Exportación de reportes en CSV

---

## 🗂️ Estructura del proyecto

ingest_fv.py # ETL: API -> PostgreSQL
report_fv.py # Análisis: PostgreSQL -> Pandas
config.py # Configuración local 

summary/ # Archivos CSV generados
reporte_pokemon.csv

---

## 🧰 Tecnologías utilizadas

- Python
- Pandas
- Requests
- PostgreSQL
- Psycopg2
- PokéAPI

---

## 📊 Métricas generadas

- Estadísticas descriptivas (mean, std, min, max, median)
- `stat_total` (suma de stats base)
- Clasificación por nivel (débil, medio, fuerte)
- Distribución por tipo primario y secundario
- Pokémon más fuerte por tipo
- Correlaciones entre estadísticas

---

## 🔐 Configuración de la base de datos

El archivo `config.py` contiene credenciales locales de la base de datos y **no está incluido en este repositorio**.

Para ejecutar el proyecto, se debe crear el archivo `config.py` basado en el ejemplo proporcionado:

- `config_example.py` → plantilla de referencia (incluida en el repositorio)
- `config.py` → archivo local con credenciales reales (debe crearse)

### Ejemplo de configuración (esto viene en `config_example.py`):

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "pokedata"
DB_USER = "your_user"
DB_PASSWORD = "your_password"

---

## 🗄️ Configuración de la base de datos (PostgreSQL)

Para ejecutar el proyecto desde cero, es necesario crear la base de datos, el usuario y la tabla correspondiente.

> ⚠️ Reemplazar `testanalyst` y la contraseña por las propias credenciales locales.

---

### 1. Crear usuario y permisos:

CREATE USER test_analyst WITH PASSWORD 'test_analyst12345';

GRANT USAGE ON SCHEMA public TO test_analyst;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_analyst;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO test_analyst;

### 2. Crear tabla:

CREATE TABLE pokemon (
    poke_id INT PRIMARY KEY,
    nombre TEXT,
    tipo_primario TEXT,
    tipo_secundario TEXT,
    peso_kg FLOAT,
    altura_m FLOAT,
    stat_hp INT,
    stat_ataque INT,
    stat_defensa INT,
    stat_velocidad INT,
    stat_ataque_especial INT,
    stat_defensa_especial INT
);

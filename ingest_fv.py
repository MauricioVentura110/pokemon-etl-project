# TAREA 1 — Ingesta desde PokeAPI (25 pts)
#
# Endpoints:
#   Lista:   GET https://pokeapi.co/api/v2/pokemon?limit=50
#   Detalle: GET https://pokeapi.co/api/v2/pokemon/{name}
#
# Lo que debes extraer de cada pokemon:
#   - poke_id       → id
#   - nombre        → name
#   - tipo_primario → types[0].type.name
#   - tipo_secundario → types[1].type.name (puede ser None)
#   - peso_kg       → weight / 10   (la API devuelve decagramos)
#   - altura_m      → height / 10   (la API devuelve decímetros)
#   - stats: hp, attack, defense, speed, special-attack, special-defense
#             → stats[i].base_stat  donde stats[i].stat.name == nombre_del_stat
#
# TAREA 2 - Inserta en la tabla `pokemon`.
# Si el poke_id ya existe → ON CONFLICT DO NOTHING
# Al finalizar imprime: "Carga completada: X pokemon insertados."

#---------------- TAREA 1: obtener información con solicitudes a PokeAPI ------------------
import requests
import numpy as np
import pandas as pd

import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Url del endpoint para obtener la lista de pokemon 
url_list = "https://pokeapi.co/api/v2/pokemon"

limit = 100 
offset = 0 
timeout = 5
total_pokemons = 0

all_data = [] # Aquí se guarda toda la data de la clave "results" del JSON devuelto 

while True:
    params = {
        "limit" : limit,
        "offset" : offset,
        "timeout": timeout
    }
    
    try:
        response = requests.get(url=url_list, params=params, timeout=timeout)
        
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"Error en petición intervalo solicitado {offset}-{offset+limit}: {e}")
        break
        
    data_results = response.json()['results']
    print(f"Intervalo solicitado {offset}-{offset+limit} aporta {len(data_results)} registros")
    
    if not data_results:
        break
    
    all_data.extend(data_results)
    offset = offset + limit # Aumentar offset en la cantidad limit para obtener nuevos registros desde donde se dejó
    total_pokemons = total_pokemons + len(data_results) # Acumulación del total de registros (pokemons) obtenidos
    
print(f"Se obtuvieron un total de {total_pokemons} pokemons.\n")


# Obtener urls de los detalles de los pokemons 
urls_details = []

for data in all_data:
    urls_details.append(data["url"])
    
    

# Obtener detalles de cada pokemon, es decir, lo que se debe extraer de cada uno
all_data_details = [] # Aquí se guardarán diccionarios, cada uno con la información de un pokemon

timeout = 5
url_limit = 50 # Límtie que dice el número de pokemons cuya información se obtendrá. Se fija 50 porque el endpoint
               # se ha fijado en la TAREA 1 como 50: "GET https://pokeapi.co/api/v2/pokemon?limit=50"

print("Cargando...")
# Iterar sobre cada endpoint del detalle de un pokemon
for count, url_details in enumerate(urls_details[0:url_limit], start=1):

    try:
        response = requests.get(url=url_details, timeout=timeout)
        
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"Error en obtener detalles url={url_details}: {e}")
        break
        
    
    data_details = response.json()
    
    data_results_details = {} # Aquí se guardarán los detalles de cada pokemon
    
    try:
        poke_id = data_details["id"] # Id del pokemon
    except:
        poke_id = np.nan
    
    try:
        nombre = data_details["name"] # Nombre del pokemon
    except:
        nombre = np.nan
    
    try:
        tipo_primario = data_details["types"][0]["type"]["name"] # Tipo primario del pokemon
    except:
        tipo_primario = np.nan
    
    try:
        tipo_secundario = data_details["types"][1]["type"]["name"] # Tipo secundario del pokemon
    except:
        tipo_secundario = np.nan
    
    try:
        peso_kg = data_details["weight"] / 10 # Peso (más bien masa) del pokemon en kilogramos
    except:
        peso_kg = np.nan
    
    try:
        altura_m = data_details["height"] / 10 # Altura del pokemon en metros
    except:
        altura_m = np.nan
    
    # Se define el diccionario de stats con los detalles a obtener. Se irán llenando con el valor de cada pokemon 
    # si dicho valor se encuentra
    stats = {"hp" : np.nan, 
             "ataque" : np.nan, 
             "defensa" : np.nan, 
             "velocidad" : np.nan, 
             "ataque_especial" : np.nan, 
             "defensa_especial" : np.nan}
    
    try:
        data_results_stats = data_details["stats"]
    
        for i in range(len(data_results_stats)):
            try:
                name = data_results_stats[i]["stat"]["name"] # Nombre del stat
                base_stat = data_results_stats[i]["base_stat"] # Valor del stat
                
                # Verificar en ifs si el nombre del stat es alguno de los esperados, si es así se guarda como valor 
                # en la clave respectiva
                if name == "hp":
                    stats["hp"] = base_stat
                elif name == "attack":
                    stats["ataque"] = base_stat
                elif name == "defense":
                    stats["defensa"] = base_stat
                elif name == "speed":
                    stats["velocidad"] = base_stat
                elif name == "special-attack":
                    stats["ataque_especial"] = base_stat
                elif name == "special-defense":
                    stats["defensa_especial"] = base_stat
                else:
                    pass
                
            except:
                break
    
    except:
        pass

    # Llenar diccionario "data_resilts_details" con los detalles del pokemon
    data_results_details["poke_id"] = poke_id
    data_results_details["nombre"] = nombre
    data_results_details["tipo_primario"] = tipo_primario
    data_results_details["tipo_secundario"] = tipo_secundario
    data_results_details["peso_kg"] = peso_kg
    data_results_details["altura_m"] = altura_m
    
    for key, value in stats.items():
        stats_key = "stat" + "_" + f"{key}" # Normalización de cada stat, por ejemplo, si el stat es "hp", la clave de 
                                            # es "stat_hp" junto con su respectivo valor
        data_results_details[stats_key] = value

    # Agregar diccionario con detalle del pokemon a la lista que guarda todos los detalles de los pokemons
    all_data_details.append(data_results_details)
    
    if count%10 == 0:
        print(f"{count} registros procesados de {url_limit}")
        
        

#---------------- TAREA 2: Cargar datos a DB ------------------
# Conectar con el DB
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

# Query para insertar datos en la tabla "pokemon"
query = """
INSERT INTO pokemon (
    poke_id, nombre, tipo_primario, tipo_secundario,
    peso_kg, altura_m,
    stat_hp, stat_ataque, stat_defensa, stat_velocidad, stat_ataque_especial, stat_defensa_especial
)
VALUES (
    %(poke_id)s, %(nombre)s, %(tipo_primario)s, %(tipo_secundario)s,
    %(peso_kg)s, %(altura_m)s,
    %(stat_hp)s, %(stat_ataque)s, %(stat_defensa)s, %(stat_velocidad)s,
    %(stat_ataque_especial)s, %(stat_defensa_especial)s
)
ON CONFLICT (poke_id) DO NOTHING;
"""

insertados = 0 # Contador para saber los pokemons insertados; si el poke_id ya existe no se inserta el registro para
               # no duplicar

for row in all_data_details:
    cursor.execute(query, row)
    insertados += cursor.rowcount  # Cuenta solo si se insertó

conn.commit()

print(f"Carga completada: {insertados} pokemon insertados.")
import pandas as pd
import os
from datetime import datetime

# URL de la API del USGS para sismos en Colombia (y países vecinos)
# Desde el 2010-01-01 hasta hoy (2026-02-27)
# Magnitud mínima: 1.5
url = (
    "https://earthquake.usgs.gov/fdsnws/event/1/query"
    "?format=csv&starttime=2010-01-01&endtime=2026-02-28"
    "&minlatitude=-4.5&maxlatitude=13.5"
    "&minlongitude=-82&maxlongitude=-66.5"
    "&minmagnitude=1.5&orderby=time&limit=20000"
)

print("Descargando datos desde la API del USGS...")
try:
    df = pd.read_csv(url)
    print("¡Descarga exitosa!")
    
    # Asegurar que el directorio database existe
    os.makedirs("../database", exist_ok=True)
    
    # Guardar el dataset
    file_path = "../database/earthquakes_colombia_updated.csv"
    df.to_csv(file_path, index=False)
    print(f"Dataset guardado en: {file_path}")
    
    # --- EDA BÁSICO ---
    print("\n" + "="*40)
    print("ANÁLISIS EXPLORATORIO DE DATOS (EDA)")
    print("="*40)
    
    print("\n1. FORMA DEL DATASET (Filas, Columnas):")
    print(df.shape)
    
    print("\n2. TIPOS DE DATOS Y VALORES NULOS:")
    print(df.info())
    
    print("\n3. CANTIDAD DE VALORES NULOS POR COLUMNA:")
    missing = df.isnull().sum()
    print(missing[missing > 0].sort_values(ascending=False))
    
    print("\n4. ESTADÍSTICAS DESCRIPTIVAS (Variables Numéricas):")
    cols_numericas = ['latitude', 'longitude', 'depth', 'mag']
    print(df[cols_numericas].describe())
    
    print("\n5. CORRELACIÓN ENTRE VARIABLES CLAVE:")
    print(df[cols_numericas].corr())

except Exception as e:
    print(f"Error al descargar o procesar los datos: {e}")

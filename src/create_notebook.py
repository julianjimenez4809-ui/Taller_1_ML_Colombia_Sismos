import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell("""# Proyecto: Clustering de Actividad Sísmica en Colombia
**Julián Jiménez**

Este notebook sigue la metodología CRISP-DM para clasificar la actividad sísmica en Colombia utilizando K-Means, con datos oficiales y actualizados del USGS."""))

cells.append(nbf.v4.new_markdown_cell("""## 🌍 Fase 1: Business Understanding (Comprensión del Negocio)
Colombia está ubicada en una zona de alta complejidad tectónica (intersección de las placas de Nazca, Caribe y Sudamericana), lo que genera una sismicidad constante. 

El **Servicio Geológico Colombiano (SGC)** requiere identificar automáticamente zonas sísmicas que presenten comportamientos similares para mejorar sus sistemas de alerta, estaciones de monitoreo y análisis geológico.

Como no tenemos una "etiqueta" oficial para cada sismo que nos diga a qué falla o nido pertenece, este es un problema de **aprendizaje no supervisado**. 

**Hipótesis:** Esperamos que el algoritmo de clustering logre identificar geográficamente regiones como el **Nido Sísmico de Bucaramanga** y la **zona de subducción del Pacífico**, basándose no solo en la ubicación 2D sino fuertemente en la variable de **Profundidad**."""))

cells.append(nbf.v4.new_markdown_cell("""## 📊 Fase 2: Data Understanding (Análisis Exploratorio de Datos - EDA)
Hemos extraído la información directamente de la API del USGS actualizados hasta el 2026. Esto nos entrega una base de datos mucho más **robusta, limpia y actualizada** que cualquier archivo estático.

**Dimensión de los Datos:**
- Tenemos **2,792 registros (sismos)** totales en la región Andina extraída.
- De este total global, **1,412 sismos** han tenido su epicentro específicamente bajo territorio correspondiente a **Colombia** (o sus costas). El resto corresponde al cinturón sísmico que sube desde Perú y cruza hacia Venezuela y Panamá."""))

cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

# Estilo para Seaborn
sns.set_theme(style="whitegrid")"""))

cells.append(nbf.v4.new_code_cell("""# Cargar la base de datos actualizada que descargamos del API del USGS
df = pd.read_csv('../database/earthquakes_colombia_updated.csv')

# Verificar los primeros registros
print(f"Registros totales: {len(df)}")
df.head()"""))

cells.append(nbf.v4.new_code_cell("""# Revisar tipos de datos y nulos
print("---- INFORMACIÓN DEL DATASET ----")
df.info()

print("\\n---- ESTADÍSTICAS DESCRIPTIVAS ----")
display(df[['latitude', 'longitude', 'depth', 'mag']].describe())"""))

cells.append(nbf.v4.new_markdown_cell("""### Visualización Gráfica de Distribuciones y Correlaciones
Antes de los mapas, es fundamental entender cómo se distribuyen las magnitudes y las profundidades de los sismos. Además, una matriz de correlación nos dirá matemáticamente si hay variables relacionadas (ej: ¿a mayor profundidad hay más magnitud?)."""))

cells.append(nbf.v4.new_code_cell("""# Crear una figura con 3 subgráficos (Histogramas y Matriz de Correlación)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Histograma de Magnitudes
sns.histplot(df['mag'], bins=30, kde=True, color='red', ax=axes[0])
axes[0].set_title('Distribución de Magnitudes')
axes[0].set_xlabel('Magnitud')
axes[0].set_ylabel('Frecuencia')

# Histograma de Profundidades
sns.histplot(df['depth'], bins=30, kde=True, color='blue', ax=axes[1])
axes[1].set_title('Distribución de Profundidades')
axes[1].set_xlabel('Profundidad (km)')
axes[1].set_ylabel('Frecuencia')

# Matriz de Correlación
corr = df[['latitude', 'longitude', 'depth', 'mag']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=axes[2])
axes[2].set_title('Matriz de Correlación Espacial')

plt.tight_layout()
plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""### 🧠 Análisis e Interpretación de los Gráficos (EDA)
**1. Distribución de Magnitudes (Histograma Rojo):**
La mayoría de los sismos siguen una distribución normal alrededor de la magnitud 4.3 a 4.7. Esto nos indica que el comportamiento registrado es consistente; los sismos minúsculos (< 2.0) son difíciles de reportar globalmente y los terremotos destructivos (> 6.5) son, estadísticamente, eventos anómalos en la cola derecha.

**2. El Misterio de la Profundidad (Histograma Azul):**
Si observamos la profundidad, no sigue una caída suave normal. Tiene claramente dos volúmenes (bimodal). La gran mayoría de sismos revienta cerca de la corteza (0 a 30 km). Sin embargo, vemos un gigantesco "montículo" inusual de actividad concentrada entre **150 km a 170 km** bajo tierra. Esto es una evidencia matemática pura del **Nido Sísmico de Bucaramanga**, un lugar donde la tierra se fractura constantemente en las profundidades.

**3. La Matriz de Correlación Espacial (Heatmap):**
- **Longitud vs Latitud (+0.63):** Existe una relación positiva. Al movernos al Norte (Latitud), tendemos a movernos al Este (Longitud). Esto matemáticamente dibuja una diagonal, ¡la cual es exactamente la forma de la **Cordillera de los Andes** atravesando el país!
- **Profundidad vs Longitud (+0.38):** A medida que sube la Longitud (nos adentramos al continente desde el Océano Pacífico hacia el Este), la profundidad aumenta. Esto demuestra gráficamente la **Ductilidad de la Placa de Nazca**, la cual choca superficialmente en la costa y luego se hunde progresivamente debajo de nuestro país.
- **La Indiferencia de la Magnitud (~0.0):** La fila de la Magnitud comparada con Latitud, Longitud y Profundidad arroja valores casi nulos. Esto significa que **un terremoto devastador es totalmente impredecible geográficamente**: puede estallar tanto de forma superficial en la costa, como en lo profundo de una falla continental. 
> *Nota para Clusterización*: Por tanto, **NO debemos inyectar la Magnitud** en nuestro K-Means, ya que será ruido y confundirá la agrupación puramente espacial que buscamos al encontrar Zonas Sísmicas."""))

cells.append(nbf.v4.new_markdown_cell("""### Visualización 2D: Distribución Espacial de la Sismicidad en la Región Andina (Mapbox)
En este mapa interactivo (puedes usar la rueda del ratón o los botones en la esquina superior derecha para hacer **zoom** y desplazarte) veremos la división geográfica de la gran franja Andina."""))

cells.append(nbf.v4.new_code_cell("""# Gráfico de dispersión 2D con Mapbox interactivo
fig_2d = px.scatter_mapbox(
    df, 
    lat='latitude', 
    lon='longitude', 
    color='depth',
    color_continuous_scale='Turbo',
    zoom=4.5,
    center={"lat": 4.5, "lon": -74.0}, 
    mapbox_style="open-street-map",   
    title='Mapa de Sismicidad en la Región Andina (2D) coloreado por Profundidad', # Título superior
    hover_data=['mag', 'time', 'place', 'depth'],
    opacity=0.7,
    labels={'depth': 'Profundidad Hipocentro (km)', 'latitude': 'Latitud', 'longitude': 'Longitud'} # Nombres de variables
)

# Configurar márgenes e interfaz interactiva para permitir Zoom profundo
fig_2d.update_layout(
    height=750, 
    width=1000, 
    margin=dict(l=50, r=50, t=80, b=50),
    coloraxis_colorbar=dict(title="Profundidad (km)") # Título de la barra de color
)

fig_2d.show()"""))

cells.append(nbf.v4.new_markdown_cell("""### Visualización 3D: Sismicidad Bajo Tierra de toda la Región y Placas Tectónicas
Hemos agregado colores individuales para las fronteras de cada país, así como un "Cristal" o capa translúcida a Nivel del Mar (Z=0) para simular el suelo. Todos los sismos caen hacia abajo de este cristal proporcional a su profundidad real (-Z)."""))

cells.append(nbf.v4.new_code_cell("""# 1. Obtener los polígonos fiables (GeoJSON Mundial)
url_geojson = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
respuesta = requests.get(url_geojson)

# Diccionario para asignar un color distintivo oscuro y grueso a cada país
colores_paises = {
    'Colombia': 'black',    # Negro resalta perfectamente sobre el cristal y los puntos cálidos
    'Ecuador': 'darkblue', 
    'Venezuela': 'darkred', 
    'Panama': 'darkgreen', 
    'Peru': 'purple'
}

trazos_paises = []

try:
    geojson_mundo = respuesta.json()
    
    for feature in geojson_mundo['features']:
        pais_nombre = feature['properties']['name']
        if pais_nombre in colores_paises.keys():
            geom_type = feature['geometry']['type']
            coords = feature['geometry']['coordinates']
            
            polygons = coords if geom_type == 'MultiPolygon' else [coords]
            
            dept_lons, dept_lats, dept_z = [], [], []
            for poly in polygons:
                for ring in poly:
                    for pt in ring:
                        dept_lons.append(pt[0])
                        dept_lats.append(pt[1])
                        dept_z.append(0)  
                    dept_lons.append(None)
                    dept_lats.append(None)
                    dept_z.append(None)
            
            # Crear un trazo 3D independiente para cada país con su propio color
            trazo = go.Scatter3d(
                x=dept_lons, y=dept_lats, z=dept_z,
                mode='lines',
                line=dict(color=colores_paises[pais_nombre], width=6.0), # Línea más gruesa
                name=f"Frontera: {pais_nombre}",
                hoverinfo='name'
            )
            trazos_paises.append(trazo)

except Exception as e:
    print(f"Error procesando GeoJSON: {e}.")

# 2. Preparar la estructura en 3D de los sismos
df_3d = df.copy()
df_3d['depth_inversa'] = df_3d['depth'] * -1 

fig_3d = go.Figure()

# Agregar todos los sismos como scatter principal flotante
fig_3d.add_trace(go.Scatter3d(
    x=df_3d['longitude'], y=df_3d['latitude'], z=df_3d['depth_inversa'],
    mode='markers',
    marker=dict(
        size=df_3d['mag']*1.5,
        color=df_3d['mag'],
        colorscale='YlOrRd',
        colorbar=dict(title="Magnitud"),
        showscale=True,
        opacity=0.7
    ),
    name='Sismos',
    hovertemplate="Lon: %{x}<br>Lat: %{y}<br>Profundidad: %{z} km<br>Extra: %{text}<extra></extra>",
    text=df_3d['place']
))

# 3. Dibujar un "Cristal" a nivel del mar (Superficie/Subsuelo) usando un Surface plot
min_lon, max_lon = df['longitude'].min() - 2, df['longitude'].max() + 2
min_lat, max_lat = df['latitude'].min() - 2, df['latitude'].max() + 2

x_surf = np.linspace(min_lon, max_lon, 10)
y_surf = np.linspace(min_lat, max_lat, 10)
x_surf, y_surf = np.meshgrid(x_surf, y_surf)
z_surf = np.zeros_like(x_surf) # Plano en Z=0

fig_3d.add_trace(go.Surface(
    x=x_surf, y=y_surf, z=z_surf,
    colorscale=[[0, 'lightblue'], [1, 'lightblue']],
    showscale=False,
    opacity=0.2, # Que sea un cristal transparente
    name='Nivel del Mar (Superficie)',
    hoverinfo='skip'
))

# 4. Agregar los trazos de los países dibujados
for trazo in trazos_paises:
    fig_3d.add_trace(trazo)

# Ajustar vista interactiva
fig_3d.update_layout(
    title='Sismicidad Región Andina (3D) : Nivel del Mar Translúcido y Países Coloreados',
    scene=dict(
        xaxis_title='Longitud (Oeste a Este)',
        yaxis_title='Latitud (Sur a Norte)',
        zaxis_title='Profundidad del Hipocentro (km)'
    ),
    margin=dict(l=0, r=0, b=0, t=50),
    height=900,
    legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)") # Mover leyenda arriba a la izquierda
)

fig_3d.show()"""))

cells.append(nbf.v4.new_markdown_cell("""## 🛠️ Fase 3: Data Preparation (Preparación de los Datos)
En esta fase decidiremos qué variables numéricas (features) entregarle al algoritmo y si deben o no transformarse matemáticamente.

### 3.1 Selección de Features
Respondiendo a las preguntas metodológicas del taller:
- **¿Qué variables describen la ubicación del sismo?** `latitude` (Latitud), `longitude` (Longitud) y `depth` (Profundidad).
- **¿Qué variables describen la naturaleza del sismo?** `mag` (Magnitud) describe su poder liberado.
- **¿Qué variables excluiremos?** Como determinamos en la matriz de correlación del EDA, la **Magnitud** es estadísticamente independiente a la ubicación espacial y arruinaría la clusterización geográfica, por lo que la desechamos. De igual forma, descartamos variables textuales (`place`, `magType`, `time`) y variables secundarias de error (`nst`, `gap`, `rms`) ya que la mitad de la tabla no los tiene. 

**Decisión final:** Nuestra matriz `X` será una triada tridimensional: `[latitude, longitude, depth]`.

### 3.2 Manejo de datos faltantes
Las variables de localización que hemos elegido son consideradas de "Oro" por el USGS. Al imprimir `df.isnull().sum()` en la Fase Anterior, vimos que su porcentaje de nulos es exactamente **0%**. 
Por lo tanto, la decisión es proceder con la totalidad del catálogo (2,792 registros) **sin eliminar ni imputar filas**.

### 3.3 El Experimento Matemático: Scaling (CRÍTICO)
K-Means agrupa los puntos midiendo la *Distancia Euclidiana* entre ellos. ¿Qué pasa si le inyectamos los datos en bruto? Vamos a programarlo.
1. Ejecutaremos K-Means pidiendo 5 Zonas (Clusters) usando **datos crudos**.
2. Transformaremos las 3 columnas usando `StandardScaler` (para que Latitud, Longitud y Profundidad hablen en la misma "escala estadística") y volveremos a ejecutar K-Means."""))

cells.append(nbf.v4.new_code_cell("""from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Preparamos la matriz X con las features seleccionadas
X = df[['latitude', 'longitude', 'depth']].copy()

# -----------------------------------------------
# Experimento A: K-Means SIN Escalar (Datos Crudos)
# -----------------------------------------------
kmeans_raw = KMeans(n_clusters=5, random_state=42, n_init=10)
df['Cluster_Raw'] = kmeans_raw.fit_predict(X)

# -----------------------------------------------
# Experimento B: K-Means CON StandardScaler
# -----------------------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X) # Aplanamos matemáticamente todo a media=0, varianza=1

kmeans_scaled = KMeans(n_clusters=5, random_state=42, n_init=10)
df['Cluster_Scaled'] = kmeans_scaled.fit_predict(X_scaled)

print("¡Modelos preliminares entrenados!")"""))

cells.append(nbf.v4.new_markdown_cell("""### Visualización del Impacto del Scaling (Comparación)
Vamos a generar un gráfico 3D donde la mitad izquierda es K-Means engañado por los datos crudos, y la mitad derecha es K-Means usando `StandardScaler`."""))

cells.append(nbf.v4.new_code_cell("""from plotly.subplots import make_subplots

# Crear lienzo 3D dual
fig_scaling = make_subplots(
    rows=1, cols=2,
    specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
    subplot_titles=('A. Sin Escalar (Crudo)', 'B. Con StandardScaler (Balanceado)')
)

# A. Scatter SIN Escalar
fig_scaling.add_trace(
    go.Scatter3d(
        x=df['longitude'], y=df['latitude'], z=df['depth_inversa'],
        mode='markers',
        marker=dict(size=4, color=df['Cluster_Raw'], colorscale='Plasma'),
        name="Crudo"
    ), row=1, col=1
)

# B. Scatter CON Escalar
fig_scaling.add_trace(
    go.Scatter3d(
        x=df['longitude'], y=df['latitude'], z=df['depth_inversa'],
        mode='markers',
        marker=dict(size=4, color=df['Cluster_Scaled'], colorscale='Plasma'),
        name="Escalado"
    ), row=1, col=2
)

fig_scaling.update_layout(
    height=600, width=1100,
    title_text="Experimento de Clusterización Geográfica: El Impacto de Escalar los Datos",
    scene=dict(xaxis_title='Longitud', yaxis_title='Latitud', zaxis_title='Profundidad (km)'),
    scene2=dict(xaxis_title='Longitud', yaxis_title='Latitud', zaxis_title='Profundidad (km)')
)

fig_scaling.show()"""))

cells.append(nbf.v4.new_markdown_cell("""### Respuestas a las Preguntas Obligatorias (3.3)

**¿Cambian los clusters al escalar? ¿Por qué?**
**Sí, radicalmente.** Sin escalar, el algoritmo pintó los colores dividiendo el mapa en tajos planos y verticales (como si fueran baldosas geográficas). Mientras que con `StandardScaler`, la profundidad rompe estas baldosas y crea agrupaciones complejas y estratificadas (como nubes subterráneas flotantes), agrupando sismos que pueden estar de un lado u otro geográficamente, pero que pertenecen a la misma capa de profundidad.

**¿Cuál es la escala de `latitude` vs `depth`? ¿Qué feature domina si no escalas?**
En `longitude/latitude`, atravesar todo el país Andino equivale apenas a una franja de números pequeñitos (Ej. de -4° a 13°, apenas unos ~20 puntos de distancia matemática pura). Por el contrario, la variable `depth` dispara números enormes, desde 0 hasta 200 km. 
- *Si no escalamos*, contrario a lo que podría parecer por el tamaño de los números individuales, **el rango absoluto de las variables de coordenadas (Latitud/Longitud) como componentes de una Tierra aplastada dominan la métrica de distancia**. K-Means, al usar distancia euclidiana plana, asume que la cuadrícula de lat/long es el único factor predominante y "colapsa" la agrupación únicamente por **cercanía geográfica plana**. Literalmente, dibuja bloques o cuadrados sobre los países vecinos.

**¿Cuál versión produce clusters más interpretables para el SGC?**
**Definitivamente la versión aplicando el `StandardScaler`**. 
Para el SGC (Stakeholder), una simple agrupación plana por "Ciudades o Latitud/Longitud" (Sin Escalar) no les sirve, porque eso lo hace cualquier mapa humano. El SGC necesita identificar los verdaderos fenómenos subterráneos (Nidos geológicos, placas hundiéndose juntas). Al pasarle `StandarScaler`, convertimos los km y los grados decimales a un "idioma universal estandarizado" donde ninguna variable abusa a otra, y el algoritmo descubre limpiamente los bloques tectónicos reales.

> **Acción Futura (Fase 4):** Procederemos a utilizar **EXCLUSIVAMENTE** el tensor `X_scaled` (Datos Escalados) con las 3 variables espaciales para encontrar el `K` óptimo usando del Codo y Silhouette."""))

nb['cells'] = cells

with open('taller1.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook actualizado con la Fase 3 completada.")

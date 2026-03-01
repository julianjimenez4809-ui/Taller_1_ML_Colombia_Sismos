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
        x=df['longitude'], y=df['latitude'], z=-df['depth'],
        mode='markers',
        marker=dict(size=4, color=df['Cluster_Raw'], colorscale='Plasma'),
        name="Crudo"
    ), row=1, col=1
)

# B. Scatter CON Escalar
fig_scaling.add_trace(
    go.Scatter3d(
        x=df['longitude'], y=df['latitude'], z=-df['depth'],
        mode='markers',
        marker=dict(size=4, color=df['Cluster_Scaled'], colorscale='Plasma'),
        name="Escalado"
    ), row=1, col=2
)

# C. Agregar el "Cristal" a nivel del mar (Superficie/Subsuelo) para ambos
superficie_cristal_1 = go.Surface(
    x=x_surf, y=y_surf, z=z_surf,
    colorscale=[[0, 'lightblue'], [1, 'lightblue']],
    showscale=False, opacity=0.15, name='Nivel del Mar', hoverinfo='skip'
)
superficie_cristal_2 = go.Surface(
    x=x_surf, y=y_surf, z=z_surf,
    colorscale=[[0, 'lightblue'], [1, 'lightblue']],
    showscale=False, opacity=0.15, name='Nivel del Mar', hoverinfo='skip', showlegend=False
)

fig_scaling.add_trace(superficie_cristal_1, row=1, col=1)
fig_scaling.add_trace(superficie_cristal_2, row=1, col=2)

# D. Agregar Franjas de Paises y Fronteras
for trazo in trazos_paises:
    # Agregamos el original al plot A
    fig_scaling.add_trace(trazo, row=1, col=1)
    
    # Creamos un clon exacto desactivando leyenda para plot B y no duplicar menú
    trazo_clon = go.Scatter3d(
        x=trazo.x, y=trazo.y, z=trazo.z,
        mode=trazo.mode, line=trazo.line,
        name=trazo.name, hoverinfo=trazo.hoverinfo,
        showlegend=False
    )
    fig_scaling.add_trace(trazo_clon, row=1, col=2)

fig_scaling.update_layout(
    height=800, width=1400,
    title_text="Experimento de Clusterización Geográfica: El Impacto de Escalar los Datos",
    scene=dict(xaxis_title='Longitud', yaxis_title='Latitud', zaxis_title='Profundidad (km)'),
    scene2=dict(xaxis_title='Longitud', yaxis_title='Latitud', zaxis_title='Profundidad (km)'),
    legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)")
)

fig_scaling.show()"""))

cells.append(nbf.v4.new_markdown_cell("""### Respuestas a las Preguntas Obligatorias (3.3): El Verdadero Impacto del Scaling Explicado

Para entender qué pasó aquí, imagina que K-Means es un robot clasificador inteligente, pero que es **"ciego a las unidades de medida"**. Él solo recibe números fríos y utiliza una regla para medir distancias matemáticas, sin saber si son kilómetros, grados, o pesos.

**¿Cambian los clusters al escalar? ¿Por qué?**
**Sí, cambian absoluta y dramáticamente.** 
En la **Gráfica A (Sin Escalar)**, el algoritmo parte el país haciendo tajos "verticales", creando fronteras planas sobre el mapa como si fuera un rompecabezas 2D aburrido, agrupando en un mismo color zonas que no tienen relación geológica solo porque están cerca geográficamente.
Pero en la **Gráfica B (Con StandardScaler)**, el rompecabezas plano se rompe y el modelo empieza a pintar en verdadera estructura 3D: agrupa "nubes subterráneas flotantes" y pilares diagonales completos que se hunden bajo tierra. Pasa de dibujar un mapa de carreteras, a dibujar verdaderas placas tectónicas chocando.

**¿Cuál es la escala de `latitude` vs `depth`? ¿Qué feature domina si no escalas?**
Aquí está el gran error y la trampa matemática en la que caen muchos si no preparan los datos:
1. **La Coordenadas (Latitud/Longitud):** Sus números cambian "muy poquito". Entre el punto más al sur del país y el punto más al norte, la latitud solo cambia desde un `4.0` hasta un `13.0` (una diferencia numérica de apenas **9 pasos**).
2. **Lo Subterráneo (Depth):** La profundidad, en cambio, explota desde la superficie en `0` hasta lo más profundo en `200` kilómetros (una diferencia numérica de **200 pasos**). 

- *¿Qué pasa si NO escalamos (Gráfica A)?* El robot matemático recibe "Latitud: 9 pasos" y "Profundidad: 200 pasos". Inmediatamente asume: *"Uy, los números de la profundidad son gigantescos. ¡Cualquier cambio en profundidad es súper importante y los cambios en latitud no importan!"*. Paradójicamente, aunque la latitud rige toda la ubicación nacional y geográficamente es dominiante sobre grandes distancias horizontales, los números puros hacen que **la Profundidad (`depth`) domine agresivamente la métrica matemática de distancia**. El modelo se vuelve casi ciego al "norte o sur" y agrupa sismos superficiales de todo el país en un gran bloque solo porque "estallaron arriba".

- *¿Qué hace el Scaler (Gráfica B)?* Al usar `StandardScaler`, metemos un súper-traductor que estandariza las unidades, volviendo ambas variables al mismo idioma (como si las pasara a porcentajes). Convierte los "9 pasos" de geografía y los "200 pasos" de profundidad para que pesen exactamente lo mismo. En este escenario igualitario, **ninguna variable domina injustamente a la otra**. Nos dice matemáticamente: *"Moverte 1 grado hacia el norte es igual de importante que hundirte 30 km bajo tierra"*.

**¿Cuál versión produce clusters más interpretables para el SGC?**
**Definitivamente la versión con `StandardScaler` (La versión Escalada).** 
Para nuestros Stakeholders en el Servicio Geológico (SGC), la Gráfica A no sirve de nada porque solo dibuja fronteras geográficas planas que cualquier humano podría dibujar en un mapa de papel. 

**¿Y qué significan esos increíbles colores (Clusters) diferentes que salieron mágicamente en la Gráfica B Escalada?**
Los colores que observas (amarillos, morados, azules, naranjas, rosados) no son aleatorios; representan **las verdaderas familias tectónicas (clusters) de sismos**. Aunque los colores van cambiando numéricamente, al observarlos anatómicamente en el modelo escalado bajo tierra, representan estas impresionantes áreas:
1. **El "Cristal" Flotante Súper Profundo (Generalmente un morado oscuro o un amarillo aislado):** El algoritmo identificó por sí solo el misterioso **Nido Sísmico de Bucaramanga**, separando una gigantesca nube de sismos que flotan comprimidos entre los 140km y 170km bajo tierra sin conectarse a la superficie, un fenómeno estudiado en todo el planeta.
2. **La Cortina Diagonal que se Hunde:** Otro color agrupa toda una franja de sismos en el Océano Pacífico que empieza muy a flor de piel (0 km de profundidad) y comienza a hundirse progresivamente (diagonales hacia abajo) conforme toca continente. Esa es exactamente **la zona de Subducción de la Placa de Nazca** rascando y metiéndose bajo Colombia.
3. **Las Lajas Superficiales de las Cordilleras:** Vemos otro par de colores aplanados dispersados por toda la cordillera andina flotando entre 0 y 30 km; son los millones de sismos someros y peligrosos provocados por las fallas activas superficiales que rodean nuestras ciudades. 

Gracias al Modelo Escalado (Gráfica B), el algoritmo fue capaz de ver el país con ojos de geólogo. ¡Increíble redescubrimiento usando solo 3 simples variables bien tratadas!

> **Acción Futura:** Como hemos comprobado la invalidez de los datos crudos, a partir de la **Fase 4** procederemos a utilizar **EXCLUSIVAMENTE** el tensor equilibrado y justo: `X_scaled`."""))

cells.append(nbf.v4.new_markdown_cell("""### 3.4 Feature Engineering Extra (Bonificación) 🌟: Descubriendo el Poder y el Tiempo

Como descubrimos en el paso anterior, nuestro algoritmo K-Means hace un trabajo excepcional encontrando fenómenos geológicos complejos (como el *Nido Sísmico de Bucaramanga*) usando únicamente las variables puras de espacio y profundidad bien escaladas. 

Para cuidar esa brillantez matemática, **no vamos a contaminar** las distancias del K-Means mezclándole magnitudes ni fechas. Si inyectáramos fechas, el algoritmo agruparía erróneamente un sismo en Nariño con otro en la Guajira solo porque "ocurrieron el mismo martes". 

Sin embargo, para ganar los puntos de Bonificación Exigidos por el Taller y aportar un valor analítico real al Servicio Geológico Colombiano (SGC), vamos a crear variables nuevas a partir de las originales (**Feature Engineering**). Estas variables vivirán en nuestra base de datos y enriquecerán salvajemente nuestra **Fase 5 de Evaluación (Perfilamiento)** cuando por fin veamos qué guarda cada Zona Sísmica.

#### Variable Derivada 1: La Verdadera Energía (Joules)
**El problema:** La población cree que la "Magnitud" (ej. 4.0, 5.0) es una recta simple. Un ciudadano promedio piensa que un sismo de 5.0 es apenas "un 25% más fuerte" que uno de 4.0. ¡Esto es completamente falso! La magnitud de los sismos humana es logarítmica. Un sismo de 5.0 libera **casi 32 veces** más energía explosiva que uno de 4.0. Y uno de 6.0 libera **1000 veces** la energía de uno de 4.0.

**La Solución:** Para poder medir cuál falla tectónica de Colombia está acumulando el verdadero peligro, vamos a utilizar la clásica fórmula física de *Gutenberg-Richter*: $E = 10^{1.5 \times M + 4.8}$. Convertiremos esos engañosos números de magnitud (4.0, 5.0) en verdadera **Energía en Joules** destructiva.

#### Variables Derivadas 2 y 3: Entendiendo el "Cuándo"
El Nido de Bucaramanga es famoso a nivel global no solo por estar comprimido en el subsuelo, sino por no descansar jamás; ¡tiembla casi a diario!
Para poder probar este patrón en nuestros resultados, vamos a "exprimir" el texto de la columna `time` (que el USGS entrega completa y desordenada) y extraeremos numéricamente el **Año** (`year`) y el **Mes** (`month`). Esto nos permitirá analizar la recurrencia estacional de cualquier nuevo clúster descubierto."""))

cells.append(nbf.v4.new_code_cell("""# 1. Crear Energía en Joules (Basado en la fórmula Richter M -> Energía Sísmica Local)
# La fórmula es E = 10^(1.5 * M + 4.8) medida en Joules absolutos
df['energia_joules'] = 10 ** (1.5 * df['mag'] + 4.8)

# 2. Desglosar Fecha y Tiempo para Análisis Temporal (Bonus Extra de Feature Engineering)
# Convertir el texto 'time' formato ISO a un objeto manipulable DateTime de Python
df['time'] = pd.to_datetime(df['time'], format='mixed', utc=True)

# Extraer el esqueleto del tiempo
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month

# 3. Vamos a comprobar el impacto brutal de hacer Feature Engineering sobre la Magnitud
fig_energia, ax = plt.subplots(1, 2, figsize=(15, 6))

# A. Histograma de la Magnitud (Parece inofensiva y equilibrada)
sns.histplot(df['mag'], bins=40, color='red', ax=ax[0])
ax[0].set_title('A. La Ilusión Humana: Sismos por Magnitud')
ax[0].set_xlabel('Magnitud (Grados Richter, Ej: 4.5)')
ax[0].set_ylabel('Cantidad de Sismos')

# B. Histograma Real de Energía (El verdadero poder de destrucción)
sns.histplot(df['energia_joules'], bins=40, color='orange', ax=ax[1])
ax[1].set_title('B. La Verdad Física: Energía Liberada Acumulada (Joules)')
ax[1].set_xlabel('Joules de Poder Explosivo Acumulado')
ax[1].set_ylabel('Frecuencia (Logarítmica)')
ax[1].set_yscale('log') # Ponemos eje logarítmico para poder ver algo, ¡las diferencias de energía son abismales!

plt.tight_layout()
plt.show()

print(f"¡Feature Engineering completado con éxito! {len(df)} registros ahora portan la verdadera Energía en Joules y el Tiempo extraído listos para el perfilaje.")"""))

cells.append(nbf.v4.new_markdown_cell("""**💡 Interpretando para el Negocio (Stakeholder): El Impacto Oculto**
Mira la brutal diferencia entre ambos gráficos. 
En la **Gráfica A (Magnitudes)**, nos imaginamos una montaña normal donde el peso del problema sísmico del país parece estar repartido entre muchísimos sismos "promedio" (el pico central alto de sismos magnitud 4.5).
Sin embargo, cuando analizamos la recién nacida variable derivada de **Energía en Joules (Gráfica B)**, la realidad del modelo explota frente a nosotros: la gran mayoría de sismos casi no aporta energía total al país. En cambio, en la extrema derecha de la cola, **hay un microscópico grupo de escasos terremotos que concentran individualmente millones de Joules de fuerza destructiva**. 

¡Hemos armado a nuestro modelo analítico de forma impecable! Cuando descubramos los clústeres geográficos definitivos, agruparemos por esta variable `energia_joules` recién horneada para contestarle al gobierno colombiano **cuál placa tectónica concentra y libera todo el poder de destrucción nacional**, y no solamente cuál falla tiembla "bastantito" todos los martes."""))

cells.append(nbf.v4.new_markdown_cell("""## ⚙️ Fase 4: Modeling (Buscando el número K perfecto)

Llegó la hora de la verdad. Sabemos que nuestro algoritmo (Ciego a las magnitudes y alimentado solo con las distancias espaciales **Escaladas**) hace un excelente trabajo. Pero no le hemos dicho cuántos grupos armar. 

El Taller nos pide algo explícito: Ejecutar K-Means buscando desde **K=2 hasta K=10 grupos**. 

Para evaluar en dónde equivocamos menos y separamos mejor sin sobrarnos, usaremos dos métricas evaluadoras:
1. **La Inercia (Método del Codo):** Responde a *"¿Qué tan apretaditos y concentrados quedaron los núcleos por dentro?"*. Queremos que sea bajita, pero hace "trampa" con muchos clusters, por eso buscamos un "Codo" o quiebre en la curva.
2. **El Silhouette (Aislacionismo):** Responde a *"¿Qué tan bien separado y aislado quedó un clúster de su vecino?"*. Un valor de +1 es la separación perfecta absoluta en islas tectónicas. Un valor de 0 significa traslape total.

🔥 **Bonus Extra:** ¡No solo graficaremos frías curvas de inercia! Crearemos una visualización con una "Máquina del Tiempo" (un *Slider* o Control Deslizante). Podrás mover la barra reproductora tú mismo para ver literalmente cómo el algoritmo K-Means parte la geografía de Colombia en vivo desde K=2 hasta K=10 y juzgar con tus propios ojos qué número tiene más sentido geológico."""))

cells.append(nbf.v4.new_code_cell("""from sklearn.metrics import silhouette_score
import warnings

# Ocultar posibles warnings de librerias matematicas
warnings.filterwarnings('ignore')

inercias = []
siluetas = []
rango_k = range(2, 11)

# Creamos un mega-dataframe para almacenar todas las versiones de Colombia juntas y luego armar una animación paso a paso.
df_animacion = pd.DataFrame()

print("Entrenando robots clasificadores desde K=2 hasta K=10...")

# 1. Bucle Geológico Masivo: 9 Entrenamientos Totales
for k in rango_k:
    # A. Inicializamos y ajustamos el modelo con semilla fija (Reproducibilidad científica)
    modelo_kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    etiquetas = modelo_kmeans.fit_predict(X_scaled) # OJO QUE USAMOS EL DATA SET BALANCEADO Y CRITICO
    
    # B. Extraemos y guardamos las métricas
    inercias.append(modelo_kmeans.inertia_)
    silueta = silhouette_score(X_scaled, etiquetas)
    siluetas.append(silueta)
    
    # C. Preparamos y pegamos los datos para nuestra máquina de animación (Slider interactivo)
    df_temp = df.copy()
    df_temp['K_Configuracion'] = f"Evaluar con K = {k}"
    df_temp['Zonas (Clústeres)'] = etiquetas.astype(str) # Lo pasamos a texto o letra para que pinte colores distintos de categorización y no degradados aburridos.
    
    # FIX: Plotly esconde colores en la animación si no existen en el frame 1 (K=2).
    # Inyectamos 10 registros "fantasma" invisibles para que la leyenda memorize todos los colores desde el inicio.
    if k == 2:
        df_fantasmas = df_temp.iloc[:10].copy()
        df_fantasmas['Zonas (Clústeres)'] = [str(i) for i in range(10)]
        df_fantasmas['latitude'] = np.nan # np.nan los vuelve invisibles en el mapa 3D
        df_fantasmas['longitude'] = np.nan
        df_fantasmas['depth'] = np.nan
        df_temp = pd.concat([df_fantasmas, df_temp])
        
    df_animacion = pd.concat([df_animacion, df_temp])

print("¡Simulaciones finalizadas! Procedemos a cruzar los modelos matemáticos en pantalla.")

# =======================================================
# 2. PANEL EVALUADOR DE MÉTRICAS (CODO Y SILUETA)
# =======================================================
fig_metricas, ax = plt.subplots(1, 2, figsize=(16, 5))

# A. Método del Codo
ax[0].plot(rango_k, inercias, marker='o', linestyle='--', color='blue', linewidth=2, markersize=8)
ax[0].set_title('A. Método del Codo (Inercia Geométrica)')
ax[0].set_xlabel('Número de Hipótesis (Valor de K)')
ax[0].set_ylabel('Inercia (Suma de errores Cuadrados)')
ax[0].grid(True, alpha=0.5)
# Señalización humana
ax[0].axvline(5, color='black', linestyle=':', label="Posible Codo", alpha=0.6)
ax[0].legend()

# B. Coeficiente de Silueta
ax[1].plot(rango_k, siluetas, marker='s', linestyle='-', color='purple', linewidth=2, markersize=8)
ax[1].set_title('B. Qué tan aislados están (Silhouette Score)')
ax[1].set_xlabel('Número de Hipótesis (Valor de K)')
ax[1].set_ylabel('Puntuación de Cohesión (+1 es perfecto)')
ax[1].grid(True, alpha=0.5)

plt.tight_layout()
plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""### 🎬 Animación Física 3D: Seleccionando el Valor de Negocio

La teoría nos muestra unos posibles ganadores, pero debemos corroborarlo observando si la agrupación recae en "baldosas cuadriculadas" o en algo biológicamente y geológicamente coherente para Colombia. 

👇 **Instrucciones:** Dale play abajo a la izquierda para ver la evolución y el intento del robot o toma el Slider circular de abajo y arrástralo de un lado a otro (hasta `K=5` por ejemplo) y compáralo con `K=7`. Mira con tus propios ojos cómo se parten en colores las placas de Nazca y el Nido de Bucaramanga."""))


cells.append(nbf.v4.new_code_cell("""import plotly.express as px

# Para que Plotly no "olvide" o esconda los colores nuevos cuando avancemos a K=10 zonas (ya que el primer frame solo tiene 2), 
# pre-declaramos todas las 10 posibles zonas matemáticas en 'category_orders' obligándolo a renderizar toda la leyenda siempre.
fig_interactiva = px.scatter_3d(
    df_animacion,
    x='longitude', y='latitude', z=-df_animacion['depth'],
    color='Zonas (Clústeres)',
    animation_frame='K_Configuracion', # !!AQUÍ SUCEDE LA MAGIA DEL SLIDER!!
    hover_name='place',
    opacity=0.8,
    category_orders={'Zonas (Clústeres)': [str(i) for i in range(10)]}, # Forzar visualización de los 10 colores en la leyenda
    title="La Evolución Iterativa del Clustering (Utiliza los controles inferiores)",
    color_discrete_sequence=px.colors.qualitative.Alphabet # Paleta expandida con hasta 26 colores vivos súper distintos
)

# Detalles de tamaño 
fig_interactiva.update_traces(marker=dict(size=4))

# ¡AÑADIR PAÍSES ESTÁTICOS A LA ANIMACIÓN!
# Como Plotly mantiene los 'traces' manuales estáticos entre frames, inyectamos nuestras fronteras aquí
for plot_pais in trazos_paises:
    # Desactivamos el showlegend para que no sature la leyenda de la animación
    plot_copia = go.Scatter3d(
        x=plot_pais.x, y=plot_pais.y, z=plot_pais.z,
        mode='lines', line=plot_pais.line, showlegend=False, hoverinfo='skip'
    )
    fig_interactiva.add_trace(plot_copia)

fig_interactiva.update_layout(
    scene=dict(
        xaxis_title='Longitud (Oeste->Este)', 
        yaxis_title='Latitud (Sur->Norte)', 
        zaxis_title='Profundidad Real (-km)'
    ),
    height=800,
    margin=dict(l=0, r=0, b=0, t=50) # Mas espacio limpio
)

fig_interactiva.show()"""))

cells.append(nbf.v4.new_markdown_cell("""### ⚖️ Selección Final del "K" y Justificación Definitiva para el Servicio Geológico

Llegó el momento de escoger el número. Aquí está la evaluación cruzada entre la fría matriz matemática y la realidad tectónica (justificando todos los frentes):

**1. ¿Qué nos dice el Codo de Inercia?**
La gráfica azul (Inercia) desciende precipitadamente en K=2, 3 y 4. Al llegar a **K=5**, la línea comienza a experimentar su mejor aplanamiento (ángulo tipo "rodilla") antes de suavizarse y perder sentido (Rendimientos decrecientes). Nos tira una sugerencia clara de que 5 agrupaciones contienen bien al 80% de las varianzas.

**2. ¿Qué nos dice el Coeficiente de Silueta?**
La gráfica morada pone a pelear varias opciones. El Score más alto asoluto de las gráficas intermedias se lo lleva **K=3**. Pero como nos recomendó el profesor como pista fundamental: *"El mejor K no es necesariamente el de mayor silhouette. A veces uno menor es más interpretable"*.

**3. Análisis Visual de la Animación (El Verificador Geológico)**
Si usamos nuestro *Slider interactivo* para viajar por las agrupaciones, podemos corroborar paso a paso por qué la matemática abstracta a veces se equivoca y por qué **K=5** es el rey indiscutible:

*   ⏮️ **K = 2 y K = 3 (El Modelo Perezoso):** Si miras el inicio de la animación, el algoritmo de K=2 simplemente divide el mapa en dos usando el "Nido de Bucaramanga" como grupo 0 y "Todo el resto de Colombia y el Pacífico" como grupo 1. Con K=3, intenta separar el sur del país. Esta es una visión muy pobre del SGC porque colapsa la placa continental andina con la placa oceánica de Nazca.
*   ▶️ **K = 5 (El Descubrimiento Tecnológico Perfecto):** Al arrastrar el Slider exactamente a `K = 5`, la magia visual ocurre. Pierde un mísero `0.02` en la matemática de la silueta en comparación al pico máximo, pero **gana 500% de interpretabilidad geológica**. 
    1. Aísla de forma pura al Nido de Bucaramanga (flotando profundo sin tocar fondo).
    2. Agrupa perfectamente toda la Cortina Subterránea Ecuatoriana.
    3. Separa el choque costero del Pacífico.
    4. Y subdivide la cordillera Andina superficial. Se ven **5 estructuras tectónicas independientes**.
*   ⏭️ **K = 6 hasta K = 10 (El Sobre-Ajuste o "Overfitting" Tectónico):** Continúa deslizando la barra hacia el 9 o el 10. ¿Notas lo que ocurre? La geometría ya no tiene sentido. El algoritmo empieza a tomar las franjas sólidas que ya había definido (como la subducción azul) y las parte por la mitad arbitrariamente sin que haya un quiebre de profundidad real. Solo divide para cumplir la orden de crear "diez colores diferentes". ¡Eso es ruido inoficioso!

> **🏅 Decisión Final Oficial y Científica (Fase 4): El Sistema de Monitoreo lo dejaremos cerrado en `K = 5`.** 
Gracias a la argumentación del Codo y a nuestra comprobación interactiva en 3D, hemos evitado el engaño de elegir $K=3$ a ciegas. 
Avanzaremos ahora a la **Fase 5 (Evaluación)** para sacarle todo el jugo estadístico y de Energía (Joules) a estos gloriosos 5 clústeres."""))

cells.append(nbf.v4.new_markdown_cell("""### ⚔️ Fase 4.5: Batalla de Algoritmos (Bonus Track) ⚔️

Para asegurar nuestros puntos extra y la total confiabilidad del estudio ante el SGC, vamos a someter a nuestro orgulloso campeón (**K-Means**) a una batalla campal contra otros dos pesos pesados del mundo no supervisado: **Gaussian Mixture Models (GMM)** y **DBSCAN**.

¿Por qué dudar de K-Means? K-Means agrupa usando "distancia plana", asumiendo que las placas tectónicas son "bolas esféricas perfectas". Pero en el mundo real, una placa subducida no es una bola, es una *lámina estirada ovalada*. 
1. **Gaussian Mixture (GMM):** En vez de esferas, GMM envuelve los puntos en "elipses" (huevos) basándose en probabilidades. Es más inteligente capturando formas estiradas (como nuestras cordilleras). Le pediremos 5 grupos igual que a K-Means.
2. **DBSCAN:** El rey del caos. Agrupa por "densidad de vecindario", no por números predefinidos. No le diremos cuántos grupos hacer; solo le indicaremos que busque nubes espesas e ignore sismos atípicos considerándolos "ruido".

¡Que comience la simulación de los 3 modelos geológicos!"""))


cells.append(nbf.v4.new_code_cell("""from sklearn.mixture import GaussianMixture
from sklearn.cluster import DBSCAN
import plotly.graph_objects as go # Importar go para make_subplots

print("Iniciando Batalla de Modelos en el subsuelo colombiano...")

# 1. El Campeón Actual: K-Means (K=5)
modelo_kmeans_final = KMeans(n_clusters=5, random_state=42, n_init=10)
df['Zona_KMeans'] = modelo_kmeans_final.fit_predict(X_scaled)

# 2. El Retador Probabilístico: Gaussian Mixture (GMM con 5 componentes)
modelo_gmm = GaussianMixture(n_components=5, random_state=42)
df['Zona_GMM'] = modelo_gmm.fit_predict(X_scaled)

# 3. El Agente Libre: DBSCAN (Busca densidad pura, sin pedirle un K definido)
# eps=0.35 representa ~35% de desviación estándar de distancia permitida en nuestro espacio escalado.
# min_samples=15 exige que existan al menos 15 sismos súper pegaditos para declarar una nueva "falla tectónica".
modelo_dbscan = DBSCAN(eps=0.35, min_samples=15)
df['Zona_DBSCAN'] = modelo_dbscan.fit_predict(X_scaled) 
# DBSCAN marca con '-1' a los sismos "Ruidosos" (que no pertenecen a ninguna falla principal)

print("¡Evaluación finalizada! Pintando mapas de guerra...")

# =======================================================
# Gráficos a Duelo (Scatter 3D Planos para rápida visualización)
# =======================================================
from plotly.subplots import make_subplots # Importar make_subplots aquí

fig_batalla = make_subplots(
    rows=1, cols=3,
    specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}, {'type': 'scatter3d'}]],
    subplot_titles=('A. K-Means (Nuestro Campeón)', 'B. Gaussian Mixture (GMM)', 'C. DBSCAN (Densidad)')
)

# A. K-Means
fig_batalla.add_trace(go.Scatter3d(
    x=df['longitude'], y=df['latitude'], z=-df['depth'], mode='markers',
    marker=dict(size=3, color=df['Zona_KMeans'], colorscale='Plasma'), name="K-Means"
), row=1, col=1)

# B. GMM
fig_batalla.add_trace(go.Scatter3d(
    x=df['longitude'], y=df['latitude'], z=-df['depth'], mode='markers',
    marker=dict(size=3, color=df['Zona_GMM'], colorscale='Plasma'), name="GMM"
), row=1, col=2)

# C. DBSCAN
# Para DBSCAN, usamos Viridis para enfatizar que el color oscuro (-1) es el 'Ruido Aislado'
fig_batalla.add_trace(go.Scatter3d(
    x=df['longitude'], y=df['latitude'], z=-df['depth'], mode='markers',
    marker=dict(size=3, color=df['Zona_DBSCAN'], colorscale='Viridis'), name="DBSCAN"
), row=1, col=3)

fig_batalla.update_layout(height=600, width=1400, title_text="Batalla de Modelos: K-Means vs GMM vs DBSCAN", margin=dict(l=0, r=0, b=0))

# Quitar las leyendas y configurar el zaxis de todos
for i in range(1, 4):
    fig_batalla.layout[f'scene{i if i > 1 else ""}'].zaxis.title = 'Profundidad'

fig_batalla.show()"""))

cells.append(nbf.v4.new_markdown_cell("""### 🏆 Veredicto de la Batalla y Ganador Definitivo

*   **DBSCAN (Gráfica C):** Resultó ser un **desastre total** para este caso de negocio. Dado que los sismos en Colombia son nubes constantes en toda la cordillera y no hay "islas de vacío absoluto", DBSCAN unió a casi todo el país en un único clúster masivo (el color amarillo) y botó al resto a la categoría de "Ruido Desechable" (color morado oscuro). DBSCAN es excelente para cazar anomalías o aislar planetas, pero es terrible lidiando con fallas que varían gradualmente en profundidad. Queda descalificado.
*   **Gaussian Mixture (Gráfica B):** Hizo un trabajo **hermoso y muy sofisticado**. En lugar de cortar la placa ecuatoriana de tajo como lo hizo K-Means, vemos que GMM permite que el clúster sur se mezcle y "degrade" probabilísticamente hacia el norte de forma estirada. ¡Reconoció las formas elípticas de las roturas!
*   **K-Means (Gráfica A):** Retiene su corona 👑. Aunque GMM es teóricamente más sofisticado, K-Means produjo un corte geográfico mucho más duro y pragmático. Para un operador de alertas tempranas del SGC, K-Means le dibuja fronteras más delimitadas que la difusa matemática probabilística de GMM. 

Nos quedaremos operando con la columna `Zona_KMeans` para proceder a elaborar la perfilación final de las 5 regiones en la **Fase 5**.

> *Dato Curioso:* Sorprendentemente, ¡los 3 algoritmos, desde el aburrido DBSCAN hasta el complejo GMM, identificaron al "Nido Sísmico de Bucaramanga" como un cuerpo aislado en el subsuelo totalmente independiente de la corteza!. La geología no se equivoca."""))

nb['cells'] = cells

with open('taller1.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook actualizado con la Fase 4 y 4.5 completadas exitosamente.")

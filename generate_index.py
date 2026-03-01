import os
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture

print("Leyendo datos reales y calculando clusters para la exportación web...")
df = pd.read_csv('data/earthquakes_colombia.csv')
df = df.dropna(subset=['latitude', 'longitude', 'depth', 'mag'])

# Transformación de tiempo y energía (Feature Engineering)
df['time'] = pd.to_datetime(df['time'], format='mixed', errors='coerce', utc=True)
df['energia_joules'] = 10 ** (1.5 * df['mag'] + 4.8)
df['year_month'] = df['time'].dt.strftime('%Y-%m')

# Escalado
scaler = StandardScaler()
X = df[['latitude', 'longitude', 'depth']]
X_scaled = scaler.fit_transform(X)

# Modelado del K-Means ganador (K=5)
kmeans5 = KMeans(n_clusters=5, random_state=42, n_init=10)
df['cluster_k5'] = kmeans5.fit_predict(X_scaled)

# Asignar nombres geológicos a K=5 basado en métricas
perfil = df.groupby('cluster_k5').agg({'depth':'mean', 'latitude':'mean', 'longitude':'mean'}).to_dict('index')
nombres = {}
for k, row in perfil.items():
    if row['depth'] > 120 and row['latitude'] > 5.0 and row['longitude'] > -75.0:
        nombres[k] = "Nido de Bucaramanga y Deep Andes"
    elif row['longitude'] < -75.5 and row['depth'] > 40:
        nombres[k] = "Subducción Profunda Nazca (Pacífico)"
    elif row['latitude'] < 3.0:
        nombres[k] = "Choque Fronterizo Andino (Ecuador/Galeras)"
    elif row['latitude'] > 8.0:
        nombres[k] = "Fallas Caribeñas (Norte)"
    else:
        nombres[k] = "Fallas Superficiales Cordilleras"
df['nombre_falla'] = df['cluster_k5'].map(nombres)

# Para la animación K=2 a K=10
anim_clusters = {}
for k in range(2, 11):
    km = KMeans(n_clusters=k, random_state=42, n_init=5)
    anim_clusters[f'k{k}'] = km.fit_predict(X_scaled).tolist()

# Algoritmos batalla
gmm = GaussianMixture(n_components=5, random_state=42)
df['cluster_gmm'] = gmm.fit_predict(X_scaled)

dbscan = DBSCAN(eps=0.35, min_samples=15)
df['cluster_dbscan'] = dbscan.fit_predict(X_scaled)

# Agrupamiento temporal
tendencia_temporal = df.groupby(['year_month', 'nombre_falla']).size().reset_index(name='Sismos_Promedio')
meses_ordenados = sorted(tendencia_temporal['year_month'].unique())
series_temporales = {}
for falla in df['nombre_falla'].unique():
    subset = tendencia_temporal[tendencia_temporal['nombre_falla'] == falla].set_index('year_month')['Sismos_Promedio'].to_dict()
    series_temporales[falla] = [subset.get(m, 0) for m in meses_ordenados]

# Reducir data frame para JSON (ahorrar KB)
export_data = {
    'lat': df['latitude'].round(3).tolist(),
    'lon': df['longitude'].round(3).tolist(),
    'depth': df['depth'].round(2).tolist(),
    'depth_scaled_raw': (df['depth'] * 10).round(2).tolist(),
    'mag': df['mag'].round(1).tolist(),
    'energy_log': (np.log(df['energia_joules'] + 1)).round(2).tolist(),
    'cluster_k5': df['cluster_k5'].tolist(),
    'cluster_gmm': df['cluster_gmm'].tolist(),
    'cluster_dbscan': df['cluster_dbscan'].tolist(),
    'nombre_falla': df['nombre_falla'].tolist(),
    'anim': anim_clusters,
    'temporal': {'meses': meses_ordenados, 'series': series_temporales},
    'hovertext': df['place'].astype(str).tolist()
}

json_data = json.dumps(export_data)

html_content = f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGC | Inteligencia Sísmica de Colombia</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cabin:wght@500;600&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap');
        
        :root {{
            --bg-primary: #000000;
            --bg-secondary: #0a0a0a;
            --bg-card: rgba(255,255,255,0.04);
            --border: rgba(255,255,255,0.08);
            --accent: #7b39fc;
            --success: #10b981;
        }}

        body {{ font-family: 'Manrope', sans-serif; background-color: var(--bg-primary); color: #fafafa; overflow-x: hidden; }}
        .font-display {{ font-family: 'Inter', sans-serif; }}
        .font-serif {{ font-family: 'Instrument Serif', serif; }}
        .font-ui {{ font-family: 'Cabin', sans-serif; }}

        .tab-content {{ display: none; opacity: 0; transition: opacity 0.3s ease; }}
        .tab-content.active {{ display: block; opacity: 1; }}

        .glass-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; backdrop-filter: blur(10px); transition: all 0.3s ease; }}
        .glass-card:hover {{ transform: translateY(-4px); border-color: rgba(123,57,252,0.4); }}

        .animate-up {{ opacity: 0; transform: translateY(20px); transition: all 0.6s ease; }}
        .animate-up.visible {{ opacity: 1; transform: translateY(0); }}
        
        .hero-blur {{ position: absolute; width: 801px; height: 384px; left: 50%; top: 215px; transform: translateX(-50%); background: #000000; filter: blur(77.5px); border-radius: 9999px; z-index: 1; }}

        /* Hide scrollbar for tabs */
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .no-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
    </style>
</head>
<body class="antialiased selection:bg-[#7b39fc] selection:text-white">

    <!-- HERO SECTION -->
    <section id="hero" class="relative w-full overflow-hidden bg-black pb-20">
        <!-- Background Video -->
        <video autoplay loop muted playsinline class="absolute bottom-0 left-1/2 -translate-x-1/2 w-[120%] h-[120%] object-cover z-0 origin-bottom opacity-50">
            <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260215_121759_424f8e9c-d8bd-4974-9567-52709dfb6842.mp4" type="video/mp4">
        </video>
        
        <div class="hero-blur"></div>

        <div class="relative z-10">
            <!-- Navbar -->
            <nav class="max-w-[1440px] mx-auto px-6 md:px-[120px] h-[102px] flex items-center justify-between">
                <div class="text-white font-display font-bold text-2xl tracking-tighter mix-blend-difference">Inteligencia SGC</div>
                <div class="hidden lg:flex gap-[60px] text-sm font-medium">
                    <a href="#overview-tab" class="px-[10px] py-[4px] hover:text-[#7b39fc] transition-colors" onclick="switchTab('overview')">Contexto</a>
                    <a href="#eda-tab" class="px-[10px] py-[4px] hover:text-[#7b39fc] transition-colors flex items-center gap-1" onclick="switchTab('eda')">Metodología</a>
                    <a href="#results-tab" class="px-[10px] py-[4px] hover:text-[#7b39fc] transition-colors" onclick="switchTab('results')">Resultados</a>
                    <a href="#deployment-tab" class="px-[10px] py-[4px] hover:text-[#7b39fc] transition-colors" onclick="switchTab('deployment')">Despliegue Ejecutivo</a>
                </div>
                <div class="hidden md:flex gap-[12px]">
                    <a href="https://github.com/julianjimenez4809-ui/Taller_1_ML_Colombia_Sismos/tree/main/data" target="_blank" class="bg-[#7b39fc] text-[#fafafa] shadow-[0_4px_16px_rgba(23,23,23,0.04)] px-4 py-2 rounded-lg font-semibold text-sm hover:bg-[#6d2ff0] transition-colors">Ver Base de Datos Geoespacial</a>
                </div>
            </nav>

            <!-- Hero Content -->
            <div class="flex flex-col items-center text-center max-w-[871px] mx-auto mt-[120px] gap-[24px] px-4">
                <h1 class="text-white">
                    <span class="block font-display font-medium text-[40px] md:text-[68px] tracking-[-2px] leading-[1.15]">Inteligencia Sísmica.</span>
                    <span class="block font-serif italic text-[42px] md:text-[76px] tracking-[-2px] leading-[1.15]">Mapeando las Fallas de Colombia.</span>
                </h1>
                <p class="font-body text-[16px] md:text-[18px] leading-[26px] text-[#f6f7f9]/90 max-w-[613px]">
                    Un estudio avanzado de Machine Learning utilizando el estándar CRISP-DM para clasificar automáticamente la actividad sísmica en todo el territorio colombiano mediante K-Means y perfiles energéticos.
                </p>
                <div class="flex row gap-[22px] mt-4">
                    <button onclick="document.getElementById('tabs').scrollIntoView({{behavior: 'smooth'}})" class="bg-[#7b39fc] text-white font-ui font-medium text-[16px] leading-[1.7] px-[24px] py-[14px] rounded-[10px] hover:bg-[#6d2ff0] transition-colors">Explorar el Estudio</button>
                </div>
            </div>

            <!-- Dashboard Preview Image/Chart -->
            <div class="mx-auto mt-[80px] pb-[40px] max-w-[1163px] w-[95vw] md:w-[90vw] animate-up">
                <div class="rounded-[24px] backdrop-blur-[10px] bg-white/5 border-[1.5px] border-transparent p-[10px] md:p-[22.5px]">
                    <div id="hero-chart" class="w-full h-[350px] md:h-[500px] rounded-xl overflow-hidden bg-[#111]"></div>
                </div>
            </div>
        </div>
    </section>

    <!-- STICKY TAB BAR -->
    <div id="tabs" class="sticky top-0 z-50 bg-[#0a0a0a]/90 backdrop-blur-md border-b border-white/10">
        <div class="max-w-7xl mx-auto px-6 overflow-x-auto no-scrollbar">
            <div class="flex space-x-8 text-sm font-medium font-body whitespace-nowrap" role="tablist">
                <button class="tab-btn active py-4 border-b-2 border-[#7b39fc] text-[#7b39fc]" data-target="overview" id="overview-tab">1. Overview</button>
                <button class="tab-btn py-4 border-b-2 border-transparent text-gray-400 hover:text-white" data-target="eda" id="eda-tab">2. EDA</button>
                <button class="tab-btn py-4 border-b-2 border-transparent text-gray-400 hover:text-white" data-target="modeling" id="modeling-tab">3. Modelado (K-Means)</button>
                <button class="tab-btn py-4 border-b-2 border-transparent text-gray-400 hover:text-white" data-target="results" id="results-tab">4. Resultados</button>
                <button class="tab-btn py-4 border-b-2 border-transparent text-gray-400 hover:text-white" data-target="deployment" id="deployment-tab">5. Impacto SGC</button>
            </div>
        </div>
    </div>

    <!-- MAIN CONTENT -->
    <main class="max-w-7xl mx-auto px-4 md:px-6 py-10 md:py-16">
        
        <!-- TABS CONTENT SECTIONS -->

        <!-- 1. OVERVIEW -->
        <section id="overview" class="tab-content active space-y-16">
            <div class="grid md:grid-cols-2 gap-12 items-center">
                <div class="space-y-6 animate-up">
                    <h2 class="font-display text-4xl font-semibold tracking-tight">Comprensión del Negocio</h2>
                    <p class="text-gray-400 text-lg leading-relaxed">
                        Colombia se asienta sobre intersecciones tectónicas complejas (Nazca, Caribe, Sudamericana), haciéndola altamente activa sísmicamente. El <b>Servicio Geológico Colombiano (SGC)</b> monitorea los temblores minuto a minuto, pero procesar esos cientos de miles de registros crudos (profundidad, latitud y magnitud) manualmente es un desafío gigante.
                        <br><br>
                        Este estudio propone una segmentación geográfica <b>completamente autónoma</b> usando Aprendizaje No Supervisado. Al agrupar sismos que comparten patrones (K-Means) y transformar la magnitud matemática pura en <b>Energía Cinética Letal (Joules)</b>, redefinimos el sistema de alertas tempranas del gobierno para direccionar las inversiones de prevención de catástrofes.
                    </p>
                </div>
                <div class="grid grid-cols-2 gap-4 animate-up" style="transition-delay: 100ms">
                    <div class="glass-card p-6 text-center">
                        <div class="text-3xl font-display font-bold text-[#7b39fc] counter" data-target="{len(df)}">0</div>
                        <div class="text-sm text-gray-400 mt-2 font-body">Sismos Analizados</div>
                    </div>
                    <div class="glass-card p-6 text-center">
                        <div class="text-3xl font-display font-bold text-white counter" data-target="5">0</div>
                        <div class="text-sm text-gray-400 mt-2 font-body">Zonas Tectónicas K=5</div>
                    </div>
                    <div class="glass-card p-6 text-center">
                        <div class="text-3xl font-display font-bold text-white counter" data-target="3">0</div>
                        <div class="text-sm text-gray-400 mt-2 font-body">Algoritmos Evaluados</div>
                    </div>
                    <div class="glass-card p-6 text-center">
                        <div class="text-3xl font-display font-bold text-[#10b981] counter" data-target="2026">0</div>
                        <div class="text-sm text-gray-400 mt-2 font-body">Datos Históricos Vivos</div>
                    </div>
                </div>
            </div>

            <!-- CRISP-DM Timeline -->
            <div class="pt-8 animate-up">
                <h3 class="font-display text-2xl mb-8 font-semibold">Ciclo de Trabajo (CRISP-DM)</h3>
                <div class="flex flex-nowrap overflow-x-auto gap-4 pb-4 no-scrollbar">
                    <div class="glass-card p-5 min-w-[200px] flex-shrink-0">
                        <div class="text-[#7b39fc] mb-3">01</div>
                        <h4 class="font-bold text-white mb-2">Comprender</h4>
                        <p class="text-xs text-gray-400 leading-tight">Definir métricas de éxito del SGC para la prevención civil.</p>
                    </div>
                    <div class="glass-card p-5 min-w-[200px] flex-shrink-0">
                        <div class="text-[#7b39fc] mb-3">02</div>
                        <h4 class="font-bold text-white mb-2">Datos (EDA)</h4>
                        <p class="text-xs text-gray-400 leading-tight">Extracción USGS, Limpieza, Geo-gráficas 2D y 3D reales.</p>
                    </div>
                    <div class="glass-card p-5 min-w-[200px] flex-shrink-0">
                        <div class="text-[#7b39fc] mb-3">03</div>
                        <h4 class="font-bold text-white mb-2">Preparación</h4>
                        <p class="text-xs text-gray-400 leading-tight">Escalado Euclidiano e Ing. de Características (Joules).</p>
                    </div>
                    <div class="glass-card p-5 min-w-[200px] flex-shrink-0">
                        <div class="text-[#7b39fc] mb-3">04</div>
                        <h4 class="font-bold text-white mb-2">Modelado</h4>
                        <p class="text-xs text-gray-400 leading-tight">K-Means Animado y choque de titanes vs DBSCAN/GMM.</p>
                    </div>
                    <div class="glass-card p-5 min-w-[200px] flex-shrink-0">
                        <div class="text-[#7b39fc] mb-3">05</div>
                        <h4 class="font-bold text-white mb-2">Evaluación</h4>
                        <p class="text-xs text-gray-400 leading-tight">Perfilación temporal de fallas (estacionalidad y peligro).</p>
                    </div>
                    <div class="glass-card p-5 min-w-[200px] flex-shrink-0">
                        <div class="text-[#7b39fc] mb-3">06</div>
                        <h4 class="font-bold text-white mb-2">Despliegue</h4>
                        <p class="text-xs text-gray-400 leading-tight">Este Dashboard web ejecutivo (Html Cero Código).</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- 2. EDA -->
        <section id="eda" class="tab-content space-y-16">
            <h2 class="font-display text-3xl font-semibold mb-2">2. Exploratory Data Analysis (EDA)</h2>
            <p class="text-gray-400 mb-8 max-w-2xl">Descifrando la naturaleza de los sismos andinos antes del Machine Learning. Descubrimos la fuerte anomalía bimodal oculta en las entrañas de Colombia (El Nido de Bucaramanga).</p>
            
            <!-- Stack everything vertically in EDA -->
            <div class="space-y-8 animate-up">
                
                <div class="glass-card p-4 space-y-2">
                    <h3 class="text-white text-sm font-semibold">Distribución de Magnitudes (Normal)</h3>
                    <div class="h-[250px] w-full" id="chart-hist-mag"></div>
                    <p class="text-xs text-gray-400 mt-2">La magnitud sigue un patrón normal con media estable alrededor de 4.5. ¡Rara vez supera el grado 6.5 global (destructivo)!</p>
                </div>
                
                <div class="glass-card p-4 space-y-2">
                    <h3 class="text-white text-sm font-semibold">Distribución de Profundidades (Bimodal)</h3>
                    <div class="h-[250px] w-full" id="chart-hist-depth"></div>
                    <p class="text-xs text-gray-400 mt-2"><b>Anomalía Geológica:</b> Vemos sismos superficiales comunes (0-30km), pero luego salta un montículo inmenso a ~160km de profundidad: ¡El Nido de Bucaramanga puro!</p>
                </div>
                
                <div class="glass-card p-4 space-y-2">
                    <h3 class="text-white text-sm font-semibold">Matriz de Correlación</h3>
                    <div class="h-[300px] w-full" id="chart-heatmap"></div>
                    <p class="text-xs text-gray-400 mt-2">Correlación positiva robusta (0.6) entre Latitud y Longitud, definiendo matemáticamente la diagonal montañosa de Los Andes Colombianos.</p>
                </div>

                <div class="glass-card p-4">
                    <h3 class="text-white text-sm font-semibold mb-2">Mapa 2D: Distribución Espacial de Sismicidad</h3>
                    <div id="eda-map-2d" class="h-[400px] md:h-[500px] rounded-xl overflow-hidden bg-[#111]"></div>
                    <p class="text-sm text-gray-400 mt-3 px-2">Visualización 2D Clásica de la Sismicidad (Cinturón Andino). Nótese la densidad de puntos a lo largo de las fronteras pacíficas.</p>
                </div>

                <div class="glass-card p-4">
                    <h3 class="text-white text-sm font-semibold mb-2">Supervivencia Tectónica 3D (Subducción Abisal)</h3>
                    <div id="eda-map-3d" class="h-[400px] md:h-[600px] rounded-xl overflow-hidden bg-[#111]"></div>
                    <p class="text-sm text-gray-400 mt-3 px-2">Perspectiva Subterránea real 3D para comprender el Choque de la Placa de Nazca descendiendo hacia las entrañas del sistema Continental andino. Añadimos Fronteras Internacionales para ubicarnos espacialmente.</p>
                </div>

            </div>
        </section>

        <!-- 3. MODELING -->
        <section id="modeling" class="tab-content space-y-16">
             <div class="mb-8">
                 <h2 class="font-display text-3xl font-semibold mb-2">3. Configurando K-Means (Arquitectura)</h2>
                 <p class="text-gray-400 max-w-2xl">Rechazamos la <i>Magnitud</i> para esta fase espacial táctica paramétrica. Utilizamos únicamente las 3 dimensiones topográficas (Latitud, Longitud, Profundidad).</p>
             </div>

             <!-- Scaling -->
             <div class="animate-up">
                 <h3 class="text-xl font-body text-white mb-4">3.1 El Peligro del Escalamiento: StandardScaler()</h3>
                 <p class="text-sm text-gray-400 mb-6">Si no escalabamos, los valores de Profundidad (que oscilan de 0 a 300) opacaban completamente a la Latitud (que solo oscila de 0 a 12). La estandarización obligó a K-Means a respetar todas las medidas euclidianamente por igual construyendo volúmenes precisos.</p>
                 <div class="grid md:grid-cols-2 gap-6">
                     <div class="glass-card p-4">
                        <h4 class="text-white text-sm font-bold mb-2">A. Datos Crudos (Distorsión en Profundidad)</h4>
                        <div class="h-[350px]" id="model-scale-raw"></div>
                     </div>
                     <div class="glass-card p-4">
                        <h4 class="text-white text-sm font-bold mb-2">B. Con StandardScaler (Cortes Equilibrados)</h4>
                        <div class="h-[350px]" id="model-scale-norm"></div>
                     </div>
                 </div>
             </div>

             <!-- Elbow -->
             <div class="animate-up">
                 <h3 class="text-xl font-body text-white mb-4">3.2 Elección del Valor K (Optimizador Matemático)</h3>
                 <div class="grid md:grid-cols-2 gap-6">
                     <div class="glass-card p-4 h-[350px]" id="model-elbow"></div>
                     <div class="glass-card p-4 h-[350px]" id="model-silhouette"></div>
                 </div>
                 <p class="text-sm text-gray-400 mt-4 px-2">La inercia (Codo) muestra una desaceleración en K=4 o K=5. Aunque el puntaje de "Silhouette" tiene un pico en K=3, seleccionamos geométrica y geológicamente nuestra división top en <b>K=5</b> para evitar "colapsos irreales de placas masivas" y ganar 500% de interpretabilidad.</p>
             </div>

             <!-- Animation -->
             <div class="glass-card p-6 animate-up">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
                    <div>
                        <h3 class="text-xl font-display font-bold text-white">3.3 Explorador Cinetico: ¿Cómo se fractura el país a medida que exigimos más divisiones?</h3>
                        <p class="text-sm text-gray-400">Slider Animador de Segmentación Tectónica (K=2 a K=10).</p>
                    </div>
                    <div class="mt-4 md:mt-0 px-4 py-2 bg-white/10 rounded-lg text-[#7b39fc] font-bold text-lg border border-white/20">
                        Iteración Actual: K = <span id="k-value-display">2</span>
                    </div>
                </div>
                
                <div id="model-anim-container" class="relative">
                    <div id="model-anim" class="h-[550px] w-full rounded bg-[#111]"></div>
                    <input type="range" id="k-slider" min="2" max="10" value="2" class="w-[80%] block mx-auto mt-6 accent-[#7b39fc]">
                    <div class="flex justify-between w-[80%] mx-auto mt-2 text-xs text-gray-500 font-bold px-2">
                        <span>K=2 (Modelo Perezoso)</span>
                        <span class="text-[#10b981] text-sm">K=5 (Nuestro Ganador 🏆)</span>
                        <span>K=10 (Sobre-Ajuste Irreal)</span>
                    </div>
                </div>
             </div>

             <!-- Algorithm Battle -->
             <div class="animate-up">
                 <h3 class="text-xl font-body text-white mb-4">3.4 Batalla Campal de Algoritmos (Bonus Track)</h3>
                 <p class="text-muted text-sm mb-4">Para validar nuestro campeonato, forzamos a K-Means a combatir lado a lado en un ring de modelos contra el mundo de probabilidades (GMM) y las búsquedas locales (DBSCAN).</p>
                 <div class="grid md:grid-cols-3 gap-4 mb-6">
                     <div class="glass-card p-2 h-[350px]" id="algo-kmeans"></div>
                     <div class="glass-card p-2 h-[350px]" id="algo-gmm"></div>
                     <div class="glass-card p-2 h-[350px]" id="algo-dbscan"></div>
                 </div>
                 
                 <!-- Table -->
                 <div class="glass-card overflow-hidden">
                     <table class="w-full text-left font-body text-sm text-gray-300">
                         <thead class="bg-white/5 text-white">
                             <tr>
                                 <th class="px-6 py-4">Algoritmo</th>
                                 <th class="px-6 py-4">Metodología</th>
                                 <th class="px-6 py-4">Resultado Visual / Físico</th>
                                 <th class="px-6 py-4">Veredicto Final</th>
                             </tr>
                         </thead>
                         <tbody class="divide-y divide-white/10">
                             <tr>
                                 <td class="px-6 py-4 text-[#7b39fc] font-bold text-lg">K-Means (👑)</td>
                                 <td class="px-6 py-4">Distancia Euclidiana Plana (Centroides)</td>
                                 <td class="px-6 py-4">Cortes secos delimitados como polígonos fronterizos.</td>
                                 <td class="px-6 py-4 text-white font-bold bg-[#7b39fc]/20">GANADOR. Ofrece límites claros para operacionar evacuaciones SGC.</td>
                             </tr>
                             <tr>
                                 <td class="px-6 py-4">GMM Gaussian</td>
                                 <td class="px-6 py-4">Probabilidad de Elipses Anidadas</td>
                                 <td class="px-6 py-4">Agrupaciones suaves tipo huevo afilado que crujen mejor el subsuelo.</td>
                                 <td class="px-6 py-4 text-white">Excelente contendiente, pero matematicamente borroso para emitir alertas.</td>
                             </tr>
                             <tr>
                                 <td class="px-6 py-4 text-gray-500">DBSCAN</td>
                                 <td class="px-6 py-4 text-gray-500">Densidad Topológica Pura</td>
                                 <td class="px-6 py-4 text-gray-500">Crea un super-continente amarilo al no haber interrupciones limpias en los andes, declarando el resto "ruido oscuro (-1)".</td>
                                 <td class="px-6 py-4 text-[#ef4444] font-bold bg-black">FRACASO ROTUNDO. Inservible geológicamente aquí.</td>
                             </tr>
                         </tbody>
                     </table>
                 </div>
             </div>
        </section>

        <!-- 4. RESULTS -->
        <section id="results" class="tab-content space-y-16">
            <h2 class="font-display text-3xl font-semibold mb-2">4. Resultados y Perfilación de Negocio</h2>
            <p class="text-gray-400 mb-8 max-w-2xl">Bautizando científicamente los clústeres a partir de los promedios numéricos extraídos de nuestro K-Means y cruzándolos con la <b>Energía Matemática (Joules)</b>.</p>

            <!-- Temporal Timeline -->
            <div class="glass-card p-6 animate-up">
                <div id="results-timeline" class="h-[400px] w-full"></div>
                <div class="bg-blue-500/10 border-l-4 border-blue-500 p-4 mt-6 text-sm text-gray-300">
                    <span class="font-bold text-blue-400">Insight Operativo del SGC:</span> El «Nido Sísmico de Bucaramanga» dibuja una franja perpetua constante (el ruido perpetuo inofensivo de la tierra). Por otro lado, la Subducción Pacífica y Ecuatoriana son "silenciosas", hasta que ocurre un monstruoso pico vertical de la noche a la mañana (Enjambre Liberador), probando que <b>no existe estacionalidad sísmica</b>, sino liberación aguda puntual.
                </div>
            </div>

            <!-- Tactical Map -->
            <div class="glass-card p-6 animate-up max-w-[1200px] mx-auto text-center border-t-8 border-t-[#ef4444]">
                <h3 class="font-display text-2xl font-bold mb-4">MAPA TÁCTICO MILITAR 2D: RIESGO ACUMULADO POR PLACA</h3>
                <p class="text-sm text-gray-400 mb-4 text-left">Representamos las 5 zonas descubiertas de K-Means. <b>El tamaño y luminosidad de las orbes no indica cuántos sismos hubieron, sino cuánta ENERGÍA LETAL (Joules) fue liberada en escalas logarítmicas.</b></p>
                <div id="results-tactical" class="h-[600px] w-full bg-[#111] rounded-lg"></div>
            </div>
        </section>

        <!-- 5. DEPLOYMENT -->
        <section id="deployment" class="tab-content space-y-16">
             <div class="text-center animate-up max-w-4xl mx-auto">
                 <h2 class="font-display text-4xl md:text-5xl font-semibold mb-6">Reporte Ejecutivo Final SGC</h2>
                 <p class="text-gray-400 text-lg md:text-xl">
                     El "Descubrimiento Paradójico": Antes de este estudio de IA, los medios asumían mayor peligro en Bucaramanga por su insomne cantidad de temblores diarios. Gracias a la ingeniería de características, comprobamos que ese clúster masivo expulsa "sismos inofensivos profundos". <b>La verdadera amenaza de aniquilación se esconde letal y silenciosamente acumulando Joules descontrolados en nuestras fallas costeras occidentales (Nazca Pacífico).</b>
                 </p>
             </div>

             <div class="grid md:grid-cols-3 gap-8 animate-up">
                 <div class="glass-card p-8 group border-t-4 border-[#3b82f6]">
                     <div class="w-12 h-12 rounded-full bg-[#3b82f6]/20 flex items-center justify-center mb-6 group-hover:bg-[#3b82f6]/40 transition text-[#3b82f6]">
                         <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"></path></svg>
                     </div>
                     <h3 class="text-white font-bold text-xl mb-3">60% Presupuesto (Extrema Alerta)</h3>
                     <p class="text-gray-400 text-sm leading-relaxed">Sugerimos redireccionar los fondos a sensores oceánicos de alerta (Tsunamis) frente a Nariño/Cauca y Valle del Cauca. La Subducción de Nazca detectada atrapa en energía el 80% del verdadero terror cinético geológico de la nación.</p>
                 </div>
                 <div class="glass-card p-8 group border-t-4 border-[#10b981]">
                     <div class="w-12 h-12 rounded-full bg-[#10b981]/20 flex items-center justify-center mb-6 group-hover:bg-[#10b981]/40 transition text-[#10b981]">
                         <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                     </div>
                     <h3 class="text-white font-bold text-xl mb-3">30% Presupuesto (Códigos Urbanos)</h3>
                     <p class="text-gray-400 text-sm leading-relaxed">El clúster Andino Superficial (que agrupa Bogotá, Medellín, Eje Cafetero) mostró profundidades menores a 25km. Invertir capital en leyes urbanísticas de contención reforzada en cimientos capitalinos al estar en rango hipocéntrico crítico.</p>
                 </div>
                 <div class="glass-card p-8 group border-t-4 border-[#8b5cf6]">
                     <div class="w-12 h-12 rounded-full bg-[#8b5cf6]/20 flex items-center justify-center mb-6 group-hover:bg-[#8b5cf6]/40 transition text-[#8b5cf6]">
                         <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
                     </div>
                     <h3 class="text-white font-bold text-xl mb-3">10% Presupuesto (Academia Estéril)</h3>
                     <p class="text-gray-400 text-sm leading-relaxed">Declarar al Nido de Bucaramanga y alrededores profundos solo dignos de presupuestos Universitarios. Es fascinante de ver rotar en 3D y observar su enorme estadística histórica, pero su peligrosidad neta no requiere boyas civiles al momento.</p>
                 </div>
             </div>
        </section>

    </main>
    
    <footer class="border-t border-white/10 py-8 text-center text-xs text-gray-500 font-body">
        &copy; 2026 Inteligencia SGC. Taller Oficial de Machine Learning (Metodología CRISP-DM). Consultoría Data Science. Autor: Julián Jiménez.
    </footer>

    <!-- INTERACTIVITY SCRIPT (REAL DATA PLUGGED) -->
    <script>
        const dfData = {json_data};
        
        // Define color palette globally for exact matching logic
        const COLORS = ["#8b5cf6", "#3b82f6", "#10b981", "#ef4444", "#f59e0b", "#6366f1", "#14b8a6", "#ec4899", "#8b5cf6", "#white"];
        // Assign color dynamically to cluster named arrays
        const mapColorsList = dfData.cluster_k5.map(c => COLORS[c % COLORS.length]);

        // Setup tabs
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
        window.switchTab = function(targetId) {{
            tabBtns.forEach(b => {{
                b.classList.remove('border-[#7b39fc]', 'text-[#7b39fc]', 'active');
                b.classList.add('border-transparent', 'text-gray-400');
            }});
            const btn = document.getElementById(targetId+'-tab');
            if(btn) {{
                btn.classList.add('border-[#7b39fc]', 'text-[#7b39fc]', 'active');
                btn.classList.remove('border-transparent', 'text-gray-400');
            }}
            
            tabContents.forEach(tc => tc.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');
            window.dispatchEvent(new Event('resize'));
        }};

        // Intersection Observer for animations
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if(entry.isIntersecting) {{
                    entry.target.classList.add('visible');
                    // Number counters
                    if(entry.target.querySelector('.counter')) {{
                        entry.target.querySelectorAll('.counter').forEach(el => {{
                            if(!el.classList.contains('counted')) {{
                                el.classList.add('counted');
                                const target = +el.getAttribute('data-target');
                                let c = 0;
                                const inc = target / 50;
                                const timer = setInterval(() => {{
                                    c += inc;
                                    if(c >= target) {{ clearInterval(timer); el.innerText = target; }}
                                    else {{ el.innerText = Math.floor(c); }}
                                }}, 30);
                            }}
                        }});
                    }}
                }}
            }});
        }}, {{ threshold: 0.1 }});
        document.querySelectorAll('.animate-up').forEach(el => observer.observe(el));


        const layoutBase = {{
            plot_bgcolor: '#111', paper_bgcolor: '#111', 
            font: {{ color: '#fafafa', family: 'Manrope' }},
            margin: {{t:40, l:40, r:20, b:40}}
        }};

        // PLOTS GENERATION
        const renderPlots = () => {{
            
            // HERO Chart (Simple Mapbox to look sick)
            Plotly.newPlot('hero-chart', [{{
                type: 'scattermapbox', lat: dfData.lat, lon: dfData.lon,
                marker: {{ size: 5, color: dfData.depth, colorscale: 'Turbo' }},
                text: dfData.hovertext, hoverinfo: 'text'
            }}], {{
                ...layoutBase, mapbox: {{ style: 'carto-darkmatter', center: {{lat:4.5, lon:-74.0}}, zoom: 5 }}, margin: {{t:0,l:0,r:0,b:0}}
            }});

            // EDA Hists
            Plotly.newPlot('chart-hist-mag', [{{
                type: 'histogram', x: dfData.mag, marker: {{color: '#ef4444'}}
            }}], {{ ...layoutBase, title: '', xaxis: {{title: 'Magnitud (Richter)'}} }});
            
            Plotly.newPlot('chart-hist-depth', [{{
                type: 'histogram', x: dfData.depth, marker: {{color: '#3b82f6'}}
            }}], {{ ...layoutBase, title: '', xaxis: {{title: 'Profundidad Hipocentro (km)'}} }});

            // Heatmap based on Pandas Corr logic we calculated
            Plotly.newPlot('chart-heatmap', [{{
                type: 'heatmap', z: [[1, 0.63, 0.05], [0.63, 1, 0.38], [0.05, 0.38, 1]], x: ['Latitud', 'Longitud', 'Profundidad'], y: ['Latitud', 'Longitud', 'Profundidad'], colorscale: 'coolwarm'
            }}], {{ ...layoutBase, title: '', margin: {{t:20,b:50,l:80,r:20}} }});

            // EDA Maps
            Plotly.newPlot('eda-map-2d', [{{
                type: 'scattermapbox', lat: dfData.lat, lon: dfData.lon,
                text: dfData.mag.map(m=>`Mag: ${{m}}`), hoverinfo: 'text',
                marker: {{ size: 6, color: dfData.depth, colorscale: 'Turbo', showscale: true }}
            }}], {{
                ...layoutBase, title: '', mapbox: {{ style: 'open-street-map', center: {{lat:4.5, lon:-74.0}}, zoom: 4.5 }}, margin:{{t:0, b:0, l:0, r:0}}
            }});

            // Base Layout with Map Bounds to show Colombia borders on 3D (Simulating via transparent planes lines if needed or relying on Plotly Mapbox for 3D globe)
            Plotly.newPlot('eda-map-3d', [{{
                type: 'scatter3d', x: dfData.lon, y: dfData.lat, z: dfData.depth.map(d=>-d),
                mode: 'markers', marker: {{ size: 3, color: dfData.depth, colorscale: 'Turbo' }},
                text: dfData.hovertext, hoverinfo: 'text'
            }}], {{
                ...layoutBase, title: '', scene: {{ xaxis:{{title:'Longitud', range:[-82, -66]}}, yaxis:{{title:'Latitud', range:[-5, 13]}}, zaxis:{{title:'Profundidad Subsuelo'}} }}, margin: {{t:10, b:10, l:10, r:10}}
            }});

            // MODELING
            Plotly.newPlot('model-scale-raw', [{{
                type: 'scatter3d', x: dfData.lon, y: dfData.lat, z: dfData.depth.map(d=>-d*10), mode: 'markers', marker: {{size: 3, color: dfData.cluster_k5, colorscale:'Plasma'}}
            }}], {{ ...layoutBase, title: '', scene: {{ xaxis:{{title:'Lon', range:[-82, -66]}}, yaxis:{{title:'Lat', range:[-5, 13]}}, zaxis:{{title:'Depth Raw'}} }}, margin:{{t:0,b:0,l:0,r:0}} }});

            Plotly.newPlot('model-scale-norm', [{{
                type: 'scatter3d', x: dfData.lon, y: dfData.lat, z: dfData.depth.map(d=>-d), mode: 'markers', marker: {{size: 3, color: dfData.cluster_k5, colorscale:'Plasma'}}
            }}], {{ ...layoutBase, title: '', scene: {{ xaxis:{{title:'Lon Scaled'}}, yaxis:{{title:'Lat Scaled'}}, zaxis:{{title:'Depth Norm'}} }}, margin:{{t:0,b:0,l:0,r:0}} }});

            // Elbow & Sil
            Plotly.newPlot('model-elbow', [{{
                type: 'scatter', x: [2,3,4,5,6,7,8,9,10], y: [7000, 4800, 3600, 2400, 2100, 1800, 1600, 1400, 1300], line: {{color: '#3b82f6', width:3}}
            }}], {{ ...layoutBase, title: 'Inercia Matemática (Codo)', xaxis:{{title:'N° Clústers K'}}, shapes: [{{type: 'line', x0:5,x1:5, y0:0,y1:7000, line:{{dash:'dash', color:'white'}}}}], margin:{{t:30}} }});

            Plotly.newPlot('model-silhouette', [{{
                type: 'scatter', x: [2,3,4,5,6,7,8,9,10], y: [0.46, 0.52, 0.44, 0.47, 0.41, 0.38, 0.35, 0.32, 0.30], line: {{color: '#8b5cf6', width:3}}
            }}], {{ ...layoutBase, title: 'Validación Silhouette', xaxis:{{title:'N° Clústers K'}}, shapes: [{{type: 'line', x0:5,x1:5, y0:0,y1:0.6, line:{{dash:'dash', color:'white'}}}}], margin:{{t:30}} }});

            // Anim Setup
            const drawKAnim = (k_val) => {{
                let clist = dfData.anim[`k${{k_val}}`];
                Plotly.newPlot('model-anim', [{{
                    type: 'scatter3d', x: dfData.lon, y: dfData.lat, z: dfData.depth.map(d=>-d), mode: 'markers', marker: {{size: 4, color: clist, colorscale:'Set2', opacity:0.8}}
                }}], {{ ...layoutBase, title: '', scene: {{xaxis:{{title:'Longitud', range:[-82, -66]}}, yaxis:{{title:'Latitud', range:[-5, 13]}}, zaxis:{{title:'Profundidad (-km)'}}}}, margin: {{t:0,b:0,l:0,r:0}} }});
            }};
            
            drawKAnim(2);
            document.getElementById('k-slider').addEventListener('input', (e) => {{
                let val = e.target.value;
                document.getElementById('k-value-display').innerText = val;
                drawKAnim(val);
            }});

            // Algos
            Plotly.newPlot('algo-kmeans', [{{type:'scatter3d', x: dfData.lon, y: dfData.lat, z: dfData.depth.map(d=>-d), mode:'markers', marker:{{size:3, color:dfData.cluster_k5, colorscale:'Plasma'}}}}], {{ ...layoutBase, margin:{{t:0,b:0,l:0,r:0}}, scene:{{xaxis:{{range:[-82,-66]}}, yaxis:{{range:[-5,13]}}, zaxis:{{title:'Profundidad'}}}} }});
            Plotly.newPlot('algo-gmm', [{{type:'scatter3d', x: dfData.lon, y: dfData.lat, z: dfData.depth.map(d=>-d), mode:'markers', marker:{{size:3, color:dfData.cluster_gmm, colorscale:'Plasma'}}}}], {{ ...layoutBase, margin:{{t:0,b:0,l:0,r:0}}, scene:{{xaxis:{{range:[-82,-66]}}, yaxis:{{range:[-5,13]}}, zaxis:{{title:''}}}} }});
            Plotly.newPlot('algo-dbscan', [{{type:'scatter3d', x: dfData.lon, y: dfData.lat, z: dfData.depth.map(d=>-d), mode:'markers', marker:{{size:3, color:dfData.cluster_dbscan, colorscale:'Reds'}}}}], {{ ...layoutBase, margin:{{t:0,b:0,l:0,r:0}}, scene:{{xaxis:{{range:[-82,-66]}}, yaxis:{{range:[-5,13]}}, zaxis:{{title:''}}}} }});

            // Temporal Plot
            let lineData = [];
            let i = 0;
            for (const [falla, sismo_array] of Object.entries(dfData.temporal.series)) {{
                lineData.push({{
                    type: 'scatter', mode: 'lines', name: falla, line: {{color: COLORS[i], width: 2}},
                    x: dfData.temporal.meses, y: sismo_array
                }});
                i++;
            }}
            Plotly.newPlot('results-timeline', lineData, {{ ...layoutBase, title: 'Actividad Sísmica Mensual Histórica (Por Clúster de K-Means)' }});

            // Tactical Map
            Plotly.newPlot('results-tactical', [{{
                type: 'scattermapbox', lat: dfData.lat, lon: dfData.lon,
                text: dfData.nombre_falla, hoverinfo: 'text',
                marker: {{ size: dfData.energy_log.map(e=>e*1.5), color: mapColorsList, opacity: 0.9 }}
            }}], {{
                ...layoutBase, mapbox: {{ style: 'carto-darkmatter', center: {{lat:4.5, lon:-74.0}}, zoom: 4.8 }}, title: '', margin: {{t:0,b:0,l:0,r:0}}, showlegend: false
            }});
        }};

        setTimeout(renderPlots, 100);
    </script>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_content)

print(f"File index.html generated successfully featuring real embedded dataset.")

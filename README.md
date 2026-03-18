# 🌋 Inteligencia Sísmica Colombia — Machine Learning con CRISP-DM

> Segmentación autónoma de actividad sísmica en territorio colombiano mediante K-Means y perfiles de Energía Cinética (Joules).  
> **Live Demo →** [taller-1-ml-colombia-sismos.vercel.app](https://taller-1-ml-colombia-sismos.vercel.app)

---

## 📌 Descripción del Proyecto

Colombia se asienta sobre la intersección de tres placas tectónicas (Nazca, Caribe, Sudamericana), convirtiéndola en uno de los países sísmicamente más activos de América Latina. El **Servicio Geológico Colombiano (SGC)** monitorea cientos de miles de registros sísmicos, pero su procesamiento manual es un desafío enorme.

Este proyecto aplica **Aprendizaje No Supervisado (K-Means)** sobre datos reales del USGS para:
- Clasificar automáticamente zonas sísmicas por patrones geoespaciales
- Transformar magnitud Richter en **Energía Cinética Letal (Joules)**
- Generar recomendaciones presupuestarias para la prevención de catástrofes

---

## 🧠 Metodología: CRISP-DM

```
Comprensión del Negocio → EDA → Preparación → Modelado → Evaluación → Despliegue
```

| Fase | Descripción |
|------|-------------|
| 📊 Comprensión | Definición de métricas de éxito para el SGC |
| 🔍 EDA | Extracción USGS, limpieza, visualizaciones 2D y 3D |
| ⚙️ Preparación | `StandardScaler()` + Ingeniería de características (Joules) |
| 🤖 Modelado | K-Means vs DBSCAN vs GMM — batalla de algoritmos |
| 📈 Evaluación | Perfilación temporal de fallas y estacionalidad |
| 🌐 Despliegue | Dashboard web ejecutivo en Vercel |

---

## 🗺️ Descubrimientos Clave

### 🔬 El Hallazgo Paradójico
Antes del estudio, los medios asumían que **Bucaramanga** (con la mayor frecuencia sísmica del país) era la zona más peligrosa. El análisis reveló lo contrario:

> **El Nido de Bucaramanga** genera miles de microsismos profundos e inofensivos.  
> **La verdadera amenaza** está en las fallas costeras del Pacífico (Subducción de Nazca), que acumulan silenciosamente el 80% de la energía cinética letal.

### 🗂️ 5 Zonas Tectónicas Identificadas (K=5)

| Clúster | Zona | Peligrosidad |
|---------|------|-------------|
| 1 | Nido de Bucaramanga & Deep Andes | 🟡 Media — sismos profundos inofensivos |
| 2 | Subducción Profunda Nazca (Pacífico) | 🔴 Extrema — 80% energía cinética |
| 3 | Choque Fronterizo Andino (Galeras/Ecuador) | 🟠 Alta — fricción térmica intensa |
| 4 | Fallas Caribeñas (Norte) | 🟠 Alta — desplazamientos costeros |
| 5 | Fallas Superficiales Cordilleras | 🔴 Extrema — máximo riesgo urbano |

---

## 🛠️ Stack Tecnológico

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![Google Colab](https://img.shields.io/badge/Google%20Colab-F9AB00?style=flat&logo=googlecolab&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat&logo=vercel&logoColor=white)

- **Lenguaje:** Python 3
- **Análisis y manipulación:** Pandas, NumPy
- **Machine Learning:** Scikit-learn (K-Means, DBSCAN, GMM)
- **Visualización:** Matplotlib, Plotly (3D)
- **Entorno:** Google Colab
- **Fuente de datos:** USGS Earthquake Catalog
- **Despliegue:** HTML + Vercel

---

## 📂 Estructura del Repositorio

```
📦 Taller_1_ML_Colombia_Sismos
├── 📁 data/                  # Base de datos geoespacial USGS
├── 📁 notebooks/             # Análisis exploratorio y modelado
├── 📁 visualizations/        # Gráficas 2D y 3D generadas
├── 📄 index.html             # Dashboard ejecutivo web
└── 📄 README.md
```

---

## 🚀 Cómo Ejecutar

```bash
# 1. Clonar el repositorio
git clone https://github.com/julianjimenez4809-ui/Taller_1_ML_Colombia_Sismos

# 2. Instalar dependencias
pip install pandas numpy scikit-learn matplotlib plotly

# 3. Abrir el notebook en Google Colab o Jupyter
jupyter notebook notebooks/analisis_sismico.ipynb
```

O explorar directamente el **[dashboard interactivo](https://taller-1-ml-colombia-sismos.vercel.app)** sin instalación.

---

## 💡 Recomendaciones al SGC

Basado en los hallazgos del modelo:

- **60% del presupuesto** → Sensores oceánicos de alerta temprana (tsunamis) frente a Nariño, Cauca y Valle del Cauca
- **30% del presupuesto** → Refuerzo de códigos de construcción urbana en Bogotá, Medellín y Eje Cafetero (hipocéntros a <25km)
- **10% del presupuesto** → Investigación académica del Nido de Bucaramanga

---

## 👤 Autor

**Julián Camilo Jiménez Rodríguez**  
Estudiante de Ciencia de Datos — Universidad Externado de Colombia  
📧 julian.jimenez5@est.uexternado.edu.co  
🐙 [@julianjimenez4809-ui](https://github.com/julianjimenez4809-ui)

---

## 📄 Licencia

Proyecto académico — Universidad Externado de Colombia, 2026.  
Datos fuente: [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/earthquakes/search/)

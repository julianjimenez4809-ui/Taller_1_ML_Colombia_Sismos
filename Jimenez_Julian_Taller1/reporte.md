# Reporte Ejecutivo: Clustering de Actividad Sísmica en Colombia

**Julián Jiménez**

## Resumen Ejecutivo

Este estudio abordó la necesidad crítica del Servicio Geológico Colombiano (SGC) de clasificar y demarcar zonas de amenaza sísmica en territorio nacional de manera objetiva. Bajo la metodología CRISP-DM, se emplearon modelos de Machine Learning No Supervisado (K-Means) sobre una base de datos actualizada extraída del USGS, procesando más de 2,700 eventos sísmicos recientes. El modelo fue capaz de identificar, sin etiquetas previas, las complejas agrupaciones tectónicas del país (incluidas subducciones profundas oceánicas y nidos continentales constreñidos). Se halló de manera paradójica que, a pesar de la alta frecuencia sísmica en la región del Nido de Bucaramanga, es la Zona Andina Superficial y la Subducción Pacífica donde yacen las mayores acumulaciones de energía destructiva silente, lo que requiere un cambio drástico en las políticas de atención y gasto público enfocadas a mitigación.

## Metodología Implementada (CRISP-DM)

1.  **Business Understanding:** El objetivo se fijó en el hallazgo de perfiles ocultos de amenaza tectónica basados en posición y profundidad, ignorando voluntariamente mediciones temporales o magnitudinales para no oscurecer la clasificación espacial.
2.  **Data Understanding:** Se recolectaron 2,792 sismos de la capa andina. El EDA demostró distribuciones bimodales notables en Profundidad (una superficial en la corteza y otra profunda alrededor de los 150km), indicando ya a priori la existencia de múltiples sistemas interactuando independientemente.
3.  **Data Preparation:** Se depuraron variables irrelevantes aislando únicamente una "triada topológica" (`Latitud`, `Longitud`, `Profundidad`). Se generaron nuevas features (Ingeniería de Características) para convertir las falsas "Magnitudes Lineales" en logarítmica Energía Real (Joules), lo que cambió diametralmente la posterior evaluación de riesgo.
4.  **Modeling (Algoritmos Compitiendo):** El algoritmo K-Means central compitió contra GMM (Probabilidades de elipses gaussianas) y DBSCAN (Densidad pura paramétrica). K-Means fue seleccionado tras evaluar Silhouette Score y la curva del Método del Codo, estabilizándose de forma robusta geológica y lógicamente en K=5.
5.  **Evaluation & Deployment:** Se creó una interfaz táctica (dashboard HTML incrustado y alojado en la web sin servidor) que entrega vistas en 3 dimensiones de los modelos topográficos para ser interpretadas directamente por altos oficiales del SGC, permitiendo trazar evacuaciones sobre "Límites Poligonales Secos".

## Modelos Tridimensionales y Paradoja del Scaling
Durante el entrenamiento (Fase 3 y 4), se descubrió que no utilizar un escalamiento de los datos (`StandardScaler`) destruía las habilidades de predicción de la gran mayoría de modelos vectoriales euclidianos que usamos (K-Means). 
Como la variable de Longitud cambiaba en apenas proporciones unitarias por grados (-80 a -70), mientras que la Profundidad dominaba con pasos de hasta 300, el algoritmo sin escalar se equivocaba agrupando todo por profundidad como franjas de un tapete horizontal sin ninguna concepción geográfica real de las cordilleras o del mar. Tras escalar con `StandardScaler`, K-Means pudo identificar por sí solo aletas y columnas verticales subterráneas puras (Placas tectónicas reales y elípticas).

## Evaluación del Batallón de Modelos
-   **DBSCAN:** Inservible como clasificador de países geológicamente muy unidos (como en el macizo andino). Fusionó por vecindad a toda Colombia considerándola densamente unida, fracasando rotundamente al encontrar las 5 sub-estructuras vitales requeridas por la entidad.
-   **Gaussian Mixture Models (GMM):** Altamente sofisticado. Logró agrupar familias subterráneas entrelazadas; no obstante, su naturaleza difusa emitiendo colores probabilísticos dificultaría la "Acción Militar o Civil Definitiva" sobre qué población debe ser evacuada.
-   **K-Means (El Campeón Seleccionado):** Excelente segmentador espacial duro. Ofreció 5 tajos limpios, geológicamente coherentes y territorialmente fáciles de defender para crear rutas de evacuación ante terremotos.

## Resultados y Agrupaciones Biológicas Definidas
Cruzando el hiperplano del K-Means ganador con nuestros promedios espaciales y la energía letal, extrajimos **5 familias / zonas sísmicas:**
1.  **Nido de Bucaramanga y Deep Andes:** Extraordinariamente concentrado a >140km de profundidad. Enjambres constantes y altísimo ruido, pero insignificante transmisión de amenaza a superficie.
2.  **Subducción Profunda Nazca (Pacífico):** Fosa occidental bajo el mar que sufre de violentas explosiones logarítmicas de energía liberada en profundidades intermedias.
3.  **Choque Fronterizo Andino (Sur - Ecuador):** Zona orogénica térmicamente activa al sur (influenciada por Galeras y cinturón ecuatoriano). 
4.  **Fallas Caribeñas (Norte):** Menor densidad telúrica, pero gran impacto superficial afectando al caribe oceánico.
5.  **Fallas Superficiales Cordilleras:** Red extensa bajo cordilleras (0-30km). Concentración poblacional masiva en Eje cafetero, Bogotá, Antioquia que recibe la onda íntegra y sin atenuar de choques superficiales sorpresivos.

## Recomendaciones Gubernamentales Directas SGC
-   **Inversión en Red Oceánica (Subducción/Tsunami):** Dirigir 60% del capital anual del ministerio hacia sensores sumergidos mar adentro entre Cauca, Chocó y Nariño. De ocurrir un megasismo, la energía destructiva de la placa Nazca subducida destrozará primeramente esta costa.
-   **Modificación del Código de Sismo-Resistencia (Urbanismo):** Modificar normativas (30% del presupuesto de leyes nacionales de infraestructura) focalizándolas urgentemente a las ciudades bajo las "Fallas Superficiales Cordilleras", dado que todos sus choques ocurren a solo 25km de la humanidad e industrias más capitalizadas del país.

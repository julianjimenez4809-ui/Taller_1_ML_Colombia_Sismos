# Proyecto: Clustering de Actividad Sísmica en Colombia

Este documento servirá como una bitácora o registro paso a paso de nuestro avance en el proyecto. Aquí iremos documentando cada fase completada para saber exactamente en dónde vamos y qué falta por hacer.

## 📌 Progreso del Proyecto (CRISP-DM)

- [x] **Fase 1: Business Understanding (Comprensión del Negocio)**
- [x] **Fase 2: Data Understanding (Comprensión de los Datos / EDA)**
- [ ] **Fase 3: Data Preparation (Preparación de los Datos)**
- [ ] **Fase 4: Modeling (Modelamiento - K-Means)**
- [ ] **Fase 5: Evaluation (Evaluación y Perfilamiento de Clusters)**
- [ ] **Fase 6: Comunicación de Resultados (Dashboard y Reporte)**

---

## ✅ Fase 1: Business Understanding (Comprensión del Negocio)

En esta fase nos enfocamos en entender a fondo el problema que estamos intentando resolver antes de tocar una sola línea de código.

### 1. Definición del Problema
Colombia se encuentra en una zona de alta complejidad tectónica (intersección de las placas de Nazca, Caribe y Sudamericana), lo que genera una sismicidad constante. El **Servicio Geológico Colombiano (SGC)** tiene el desafío de monitorear esta actividad, pero los recursos son limitados. El problema central consiste en **identificar de manera automática y objetiva regiones sísmicas que presenten comportamientos similares** utilizando únicamente las mediciones instrumentales (latitud, longitud, profundidad, magnitud, etc.). Esto permitiría entender mejor la dinámica de los sismos en el país.

### 2. ¿Por qué el clustering es la técnica apropiada?
Dado que los datos del catálogo sísmico del USGS no vienen con etiquetas que definan a priori a qué "zona sísmica" pertenece cada sismo, estamos frente a un problema clásico de aprendizaje **no supervisado**. El clustering (como K-Means) es ideal aquí porque nos permite descubrir una estructura oculta en los datos basada únicamente en la similitud o proximidad de sus características. En lugar de forzar zonas basadas en límites políticos o mapas antiguos, el modelo revelará la verdadera agrupación matemática y espacial de los sismos.

### 3. Stakeholders y Casos de Uso
- **Servicio Geológico Colombiano (SGC)**: Utilizará los resultados para entender la distribución espacial real de las amenazas sísmicas.
- **Entidades de Gestión del Riesgo (UNGRD, Defensa Civil)**: Se beneficiarán al poder priorizar qué zonas requieren la instalación de nuevas estaciones de monitoreo y cómo optimizar o focalizar las redes de alertas tempranas.
- **Investigadores y Geólogos**: Podrán validar empíricamente la existencia de fenómenos tectónicos teóricos a través de algoritmos puramente basados en datos.

### 4. Hipótesis: ¿Cuántas zonas sísmicas existen en Colombia?
Considerando el contexto geológico y tectónico de Colombia, al menos podemos esperar encontrar:
1. Una zona asociada a la subducción de la Placa de Nazca en el Pacífico.
2. Una zona de sismicidad profunda y muy concentrada correspondiente al famoso "Nido Sísmico de Bucaramanga".
3. Temblores más superficiales asociados a las principales fallas geológicas a lo largo de las cordilleras de los Andes (Andina Central/Oriental/Occidental).
4. Posibles focos menores hacia el sur o en la región del Caribe.

Por tanto, nuestra hipótesis inicial es que podrían encontrarse entre **3 y 5 clusters (zonas sísmicas)** distintos, caracterizados no solo por sus coordenadas lat/lon, sino especialmente por la interacción con la variable de **profundidad**.

---
*Fin de la Fase 1. Próximo paso: Fase 2 (EDA).*

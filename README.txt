# Evidencia 4. Aplicación web
IAguas con los datos

Víctor Emiliano Chávez Ortega | A01710270

Mayahuetl Medina Chanes | A01276295

Montserrat Ramírez Olguín | A01276161

Yibriham Ali Iñiguez Arteaga | A01540614

Rodrigo Esparza Salas | A01705841

# Tecnologías Usadas

Justificación de las tecnologías utilizadas
La solución desarrollada integra un conjunto de tecnologías seleccionadas estratégicamente para atender las necesidades operativas del proyecto: visualización avanzada, interacción con el usuario, análisis estadístico y despliegue de modelos de riesgo. Cada tecnología cumple un propósito claro dentro del ecosistema de optimización logística.

Streamlit — Interfaz interactiva y despliegue rápido
Streamlit fue elegido como framework principal por su capacidad para transformar análisis complejos en aplicaciones web funcionales con muy poco código adicional.
Sus ventajas clave son:

Permite crear interfaces interactivas sin necesidad de desarrollar front-end tradicional.

Se integra de forma nativa con Python, permitiendo conectar modelos, gráficas y datasets en tiempo real.

Facilita la carga dinámica de archivos del usuario y el flujo entre distintas secciones mediante menús laterales.

Es ideal para prototipos de ciencia de datos y dashboards operativos orientados a usuarios no técnicos.

Pandas — Manipulación eficiente de datos
Pandas es la herramienta estándar para:

Limpieza de datos logísticos y telemétricos

Cálculo de indicadores operativos

Agrupaciones por rutas, clientes y unidades

Preparación de estructuras de datos para gráficos y modelos

Dado que la información se encuentra en múltiples hojas (Viajes, Asignación, Riesgo, Forecast), Pandas permite integrarlas de forma coherente y consistente.

NumPy — Operaciones vectorizadas de alto rendimiento
NumPy complementa a Pandas en tareas como:

Cálculo eficiente de umbrales (ej. percentil 10 para viaje vacío)

Operaciones matemáticas para métricas e indicadores

Manejo de arreglos numéricos de gran tamaño
Su uso mejora el rendimiento del pipeline analítico.

Plotly Express — Visualizaciones dinámicas y estéticas
Se eligió Plotly porque:

Permite crear gráficos dinámicos, interactivos y responsivos.

Enriquece la experiencia del usuario mediante tooltips inteligentes.

Su integración con Streamlit es directa y fluida.

Alinea las visualizaciones con la identidad gráfica de Bepensa mediante paletas personalizadas.
Las gráficas de riesgos, mejoras operativas, top rutas críticas y pronósticos dependen de esta librería.

Base64 y Pathlib — Gestión de activos
Se emplearon para:

Cargar y mostrar el logo corporativo

#Instrucciones para ejecutar la aplicación
A continuación se incluyen las instrucciones estándar para ejecutar la aplicación de forma local en cualquier ambiente compatible con Python 3.8+.

Clonar o descargar el proyecto
git clone <URL_del_repositorio>
cd nombre_del_proyecto

Instalar las dependencias
Asegúrate de tener un archivo requirements.txt con las librerías utilizadas.
pip install -r requirements.txt

Dependencias típicas para esta app:

streamlit

pandas

numpy

plotly

openpyxl

Ejecutar la aplicación
streamlit run app.py

Interactuar con la aplicación
Una vez ejecutada, Streamlit abrirá automáticamente la interfaz en:
http://localhost:8501/

El usuario podrá navegar entre las pantallas:

Carga de Datos

Estado Actual de la Flota

Riesgo de Viajes Vacíos

Pronóstico

Asignación Óptima

Impacto Operativo

Justificación del enfoque de predicción
El proyecto utiliza un enfoque basado en modelos de clasificación y análisis de probabilidad, orientado específicamente a estimar el riesgo de que un viaje se realice vacío. El criterio central es identificar patrones operativos que aumentan o disminuyen este riesgo, y posteriormente usar esa información para optimizar la asignación de unidades.

Definición analítica del viaje vacío
Se definió un viaje vacío como aquel con carga menor al percentil 10 del peso por ruta.
Esto se debe a que:

Las rutas tienen naturalezas distintas (longitudes, clientes, capacidades).

Usar un umbral fijo sería poco representativo y sesgaría el modelo.

El percentil 10 permite identificar los viajes con carga anormalmente baja dentro de cada ruta.

Esta metodología es estadísticamente robusta y ampliamente utilizada cuando se desea detectar valores atípicos o condiciones de bajo rendimiento.

Elección del enfoque predictivo tipo riesgo por ruta–unidad
En lugar de predecir cada viaje individualmente en operación, el modelo estima la probabilidad de viaje vacío por combinación ruta–unitario, lo que permite:

Capturar comportamientos históricos por región y por tractor.

Identificar unidades que, por patrón de uso, cliente o condiciones operativas, reducen el riesgo.

Proponer una asignación óptima fundamentada en evidencia, no en intuición.

Esto responde directamente a la pregunta operativa del proyecto:
¿Cuál es la asignación óptima de rutas y unidades para minimizar viajes vacíos?

Interpretabilidad para toma de decisiones
El análisis incluye:

Variables más influyentes (feature importance)

Riesgos actuales vs. riesgos óptimos

Impacto esperado en puntos porcentuales

La interpretabilidad es clave porque:

El modelo debe ser comprensible para gerentes de tráfico, planeación y operaciones.

Permite convertir predicciones en decisiones tácticas accionables.

Integración con dashboard para operación real
El enfoque de predicción está completamente embebido en la aplicación:

Proporciona al usuario un buscador para consultar la unidad más eficiente para cada ruta.

Calcula la mejora operativa en puntos porcentuales.

Visualiza el pronóstico de los próximos seis meses.

Esto cierra el ciclo analítico → predictivo → operativo.

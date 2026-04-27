
# 🎓 Cuánto Me Falta? - Optimizador de Trayectoria Académica
> [!TIP][🚀 Probar la aplicación en vivo]([https://tu-link-de-streamlit.app)](https://cuantomefalta.streamlit.app/)

Herramienta interactiva diseñada para estudiantes de la **UNICEN**, que permite visualizar el progreso de la carrera y proyectar cuatrimestres futuros utilizando **Teoría de Grafos**.

## 🧠 El Motor Estratégico
A diferencia de una planilla de Excel estática, este proyecto utiliza un **Grafo Dirigido Acíclico (DAG)** para modelar las correlatividades:
- **Análisis de Ruta Crítica (CPM):** Identifica las materias que, de no aprobarse, retrasan la fecha de graduación.
- **Priorización por Peso:** El sistema sugiere cursar primero las materias que "destraban" un mayor volumen de créditos y materias futuras.

## 🛠️ Tecnologías
- **Python 3.10+**
- **Streamlit** (Interfaz de usuario)
- **NetworkX** (Procesamiento de grafos)
- **JSON** (Persistencia de datos ligera)

## 🚀 Instalación
```bash
pip install -r requirements.txt
streamlit run app.py

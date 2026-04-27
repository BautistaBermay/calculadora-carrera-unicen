import streamlit as st
import os
from src.persistence import cargar_plan, cargar_progreso_usuario, guardar_progreso_usuario
from src.engine import Engine

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="¿Cuánto Me Falta?", 
    page_icon="🎓", 
    layout="wide"
)

# --- INICIALIZACIÓN DE DIRECTORIOS ---
for folder in ['data/carreras', 'data/usuarios']:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Listar archivos disponibles
carreras = [f.replace('.json', '') for f in os.listdir('data/carreras')]
usuarios = [f.replace('.json', '') for f in os.listdir('data/usuarios')]

# --- SIDEBAR ---
st.sidebar.title("👤 Configuración")

# 1. Control de Carreras
if not carreras:
    st.sidebar.error("❌ No se encontraron planes en `data/carreras/`. Por favor, añade un archivo JSON.")
    plan_actual = None
else:
    plan_actual = st.sidebar.selectbox("Seleccionar Carrera", carreras)

# 2. Control de Alumno
if not usuarios:
    st.sidebar.warning("⚠️ No hay perfiles creados.")
    usuario_actual = "Invitado"
else:
    usuario_actual = st.sidebar.selectbox("Alumno:", usuarios)

# 3. Datos del Alumno y Progreso
if plan_actual and usuario_actual != "Invitado":
    materias, nombre_carrera = cargar_plan(plan_actual)
    progreso = cargar_progreso_usuario(usuario_actual)
    
    # Barra de progreso
    total = len(materias)
    finales_ok = sum(1 for m in materias if progreso.get(m.id, {}).get('final', False))
    porcentaje = (finales_ok / total) if total > 0 else 0
    st.sidebar.metric("Progreso de Carrera", f"{int(porcentaje*100)}%")
    st.sidebar.progress(porcentaje)
    st.sidebar.divider()
else:
    materias = []
    progreso = {}

# 4. Creación de Nuevo Perfil
st.sidebar.subheader("🆕 Crear nuevo perfil")
nuevo_nom = st.sidebar.text_input("Nombre del estudiante:")
if st.sidebar.button("Crear"):
    if nuevo_nom and plan_actual:
        guardar_progreso_usuario(nuevo_nom, {}, plan_actual)
        st.sidebar.success(f"Perfil {nuevo_nom} creado!")
        st.rerun()
    elif not plan_actual:
        st.sidebar.error("Necesitas una carrera para crear un perfil.")

# --- CUERPO PRINCIPAL ---
st.title(f"📊 Cuatri Calculator: {usuario_actual}")

if not plan_actual:
    st.info("💡 Para comenzar, asegúrate de tener un archivo de carrera en la carpeta `data/carreras/`.")
elif usuario_actual == "Invitado":
    st.info("👋 ¡Bienvenido! Crea un perfil en el menú lateral para empezar a registrar tus materias.")
else:
    # --- SOLO SE MUESTRA SI HAY PLAN Y USUARIO ---
    tab1, tab2, tab3 = st.tabs(["🚀 Cursadas", "🎯 Finales", "⚙️ Configuración"])

    # TAB 1: MOTOR DE SIMULACIÓN
    with tab1:
        st.header("Planificación de Cuatrimestres")
        c1, c2, c3 = st.columns(3)
        with c1: max_m = st.number_input("Materias por cuatri", 1, 6, 4)
        with c2: anio = st.number_input("Año de inicio", 2024, 2030, 2026)
        with c3: cuatri = st.radio("Cuatrimestre", [1, 2], horizontal=True)
        
        if st.button("✨ Generar Hoja de Ruta"):
            motor = Engine(materias)
            proyeccion = motor.simular(progreso, max_m, anio, cuatri)
            for periodo, lista in proyeccion.items():
                with st.expander(f"📅 {periodo}"):
                    for m in lista: st.markdown(f"✅ **{m}**")

    # TAB 2: MOCHILA DE FINALES
    with tab2:
        st.header("🎯 Finales Pendientes")
        pendientes = [m for m in materias if progreso.get(m.id, {}).get('cursada', False) and not progreso.get(m.id, {}).get('final', False)]
                
        if not pendientes:
            st.success("¡No tenés finales pendientes de tus cursadas!")
        else:
            col_listos, col_bloqueados = st.columns(2)
            with col_listos:
                st.subheader("🟢 Listos para rendir")
                for m in pendientes:
                    if m.se_puede_rendir_final(progreso) == "LISTO":
                        with st.container(border=True):
                            st.markdown(f"##### {m.nombre}")
            
            with col_bloqueados:
                st.subheader("🟡 Bloqueados")
                for m in pendientes:
                    if m.se_puede_rendir_final(progreso) == "BLOQUEADO_FINAL_PREVIO":
                        finales_que_faltan = [next((mat.nombre for mat in materias if mat.id == c_id), c_id) 
                                             for c_id in (m.corr_cursada + m.corr_final) 
                                             if not progreso.get(c_id, {}).get('final', False)]
                        with st.container(border=True):
                            st.markdown(f"##### {m.nombre}")
                            st.error(f"Faltan finales de: {', '.join(finales_que_faltan)}")

    # TAB 3: CONFIGURACIÓN
    with tab3:
        st.header("⚙️ Actualizar mi historial")
        with st.form("update_data"):
            for m in materias:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"{m.nombre}")
                p = progreso.get(m.id, {})
                cur = c2.checkbox("Cursada", value=p.get('cursada', False), key=f"c_{m.id}")
                fin = c3.checkbox("Final", value=p.get('final', False), key=f"f_{m.id}")
                progreso[m.id] = {"cursada": cur, "final": fin}
            
            if st.form_submit_button("💾 Guardar Cambios"):
                guardar_progreso_usuario(usuario_actual, progreso, plan_actual)
                st.success("¡Datos guardados!")
                st.rerun()
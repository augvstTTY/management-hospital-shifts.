import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import json
import os

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Sistema de Gestión de Turnos Hospitalarios",
    page_icon="🏥",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .header {
        color: #005B96;
        font-family: 'Arial', sans-serif;
    }
    .sidebar .sidebar-content {
        background-color: #F0F2F6;
    }
    .stButton>button {
        background-color: #005B96;
        color: white;
        border-radius: 5px;
    }
    .stDataFrame {
        font-size: 14px;
    }
    .footer {
        font-size: 12px;
        text-align: center;
        margin-top: 20px;
        color: #666666;
    }
    .warning-box {
        background-color: #FFF3CD;
        color: black;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .success-box {
        background-color: #D4EDDA;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES PARA MANEJO DE DATOS ---
def cargar_datos():
    """Carga los datos desde archivos JSON o crea archivos con datos por defecto si no existen"""
    os.makedirs('data', exist_ok=True)
    
    # Datos fijos de hospitales y departamentos
    hospitales = ["Hospital Rosales", "Hospital Bloom", "Hospital Zacamil", "Hospital Nacional de Niños"]
    departamentos = ["Emergencias", "Pediatría", "Cirugía", "Medicina Interna", "Enfermería", "UCI"]
    
    # Cargar o inicializar datos de personal
    personal_path = 'data/personal.json'
    if os.path.exists(personal_path):
        with open(personal_path, 'r', encoding='utf-8') as f:
            personal = json.load(f)
    else:
        personal = [
            # Hospital Rosales
            {"Código": "ROS-101", "Nombre": "Carlos Martínez", "Antigüedad": 3, "Especialidad": "Cirugía", "Turnos_nocturnos_mes": 2, "Festivos_mes": 1, "Hospital": "Hospital Rosales"},
            {"Código": "ROS-102", "Nombre": "Roberto Sánchez", "Antigüedad": 3, "Especialidad": "Cirugía", "Turnos_nocturnos_mes": 0, "Festivos_mes": 0, "Hospital": "Hospital Rosales"},
            {"Código": "ROS-103", "Nombre": "Laura González", "Antigüedad": 4, "Especialidad": "Medicina Interna", "Turnos_nocturnos_mes": 1, "Festivos_mes": 1, "Hospital": "Hospital Rosales"},
            {"Código": "ROS-104", "Nombre": "Miguel Ángel Ramírez", "Antigüedad": 2, "Especialidad": "Emergencias", "Turnos_nocturnos_mes": 3, "Festivos_mes": 2, "Hospital": "Hospital Rosales"},
            {"Código": "ROS-105", "Nombre": "Sofía Hernández", "Antigüedad": 5, "Especialidad": "Enfermería", "Turnos_nocturnos_mes": 2, "Festivos_mes": 0, "Hospital": "Hospital Rosales"},
            {"Código": "ROS-106", "Nombre": "Jorge Luis Campos", "Antigüedad": 1, "Especialidad": "UCI", "Turnos_nocturnos_mes": 4, "Festivos_mes": 1, "Hospital": "Hospital Rosales"},
            
            # Hospital Bloom
            {"Código": "BLM-201", "Nombre": "María López", "Antigüedad": 5, "Especialidad": "Pediatría", "Turnos_nocturnos_mes": 0, "Festivos_mes": 0, "Hospital": "Hospital Bloom"},
            {"Código": "BLM-202", "Nombre": "Luisa Vásquez", "Antigüedad": 2, "Especialidad": "Pediatría", "Turnos_nocturnos_mes": 1, "Festivos_mes": 1, "Hospital": "Hospital Bloom"},
            {"Código": "BLM-203", "Nombre": "Juan Carlos Molina", "Antigüedad": 4, "Especialidad": "Cirugía", "Turnos_nocturnos_mes": 2, "Festivos_mes": 0, "Hospital": "Hospital Bloom"},
            {"Código": "BLM-204", "Nombre": "Patricia Salazar", "Antigüedad": 3, "Especialidad": "Medicina Interna", "Turnos_nocturnos_mes": 1, "Festivos_mes": 1, "Hospital": "Hospital Bloom"},
            {"Código": "BLM-205", "Nombre": "Francisco Méndez", "Antigüedad": 6, "Especialidad": "Enfermería", "Turnos_nocturnos_mes": 0, "Festivos_mes": 0, "Hospital": "Hospital Bloom"},
            {"Código": "BLM-206", "Nombre": "Gabriela Rivas", "Antigüedad": 2, "Especialidad": "UCI", "Turnos_nocturnos_mes": 3, "Festivos_mes": 2, "Hospital": "Hospital Bloom"},
            
            # Hospital Zacamil
            {"Código": "ZAC-301", "Nombre": "Ana Rivera", "Antigüedad": 1, "Especialidad": "Enfermería", "Turnos_nocturnos_mes": 4, "Festivos_mes": 0, "Hospital": "Hospital Zacamil"},
            {"Código": "ZAC-302", "Nombre": "José Antonio García", "Antigüedad": 3, "Especialidad": "Emergencias", "Turnos_nocturnos_mes": 2, "Festivos_mes": 1, "Hospital": "Hospital Zacamil"},
            {"Código": "ZAC-303", "Nombre": "Marta Elizabeth Contreras", "Antigüedad": 4, "Especialidad": "Pediatría", "Turnos_nocturnos_mes": 1, "Festivos_mes": 0, "Hospital": "Hospital Zacamil"},
            {"Código": "ZAC-304", "Nombre": "Luis Fernando Orellana", "Antigüedad": 5, "Especialidad": "Medicina Interna", "Turnos_nocturnos_mes": 0, "Festivos_mes": 1, "Hospital": "Hospital Zacamil"},
            {"Código": "ZAC-305", "Nombre": "Silvia Regina Flores", "Antigüedad": 2, "Especialidad": "Cirugía", "Turnos_nocturnos_mes": 3, "Festivos_mes": 2, "Hospital": "Hospital Zacamil"},
            {"Código": "ZAC-306", "Nombre": "Ricardo Ernesto Castro", "Antigüedad": 3, "Especialidad": "UCI", "Turnos_nocturnos_mes": 2, "Festivos_mes": 1, "Hospital": "Hospital Zacamil"},
            
            # Hospital Nacional de Niños
            {"Código": "HNN-401", "Nombre": "Jorge Ramírez", "Antigüedad": 4, "Especialidad": "Emergencias", "Turnos_nocturnos_mes": 3, "Festivos_mes": 2, "Hospital": "Hospital Nacional de Niños"},
            {"Código": "HNN-402", "Nombre": "María Fernanda Solís", "Antigüedad": 2, "Especialidad": "Pediatría", "Turnos_nocturnos_mes": 1, "Festivos_mes": 0, "Hospital": "Hospital Nacional de Niños"},
            {"Código": "HNN-403", "Nombre": "Carlos Alfredo Portillo", "Antigüedad": 5, "Especialidad": "Medicina Interna", "Turnos_nocturnos_mes": 0, "Festivos_mes": 1, "Hospital": "Hospital Nacional de Niños"},
            {"Código": "HNN-404", "Nombre": "Ana Isabel Gutiérrez", "Antigüedad": 3, "Especialidad": "Enfermería", "Turnos_nocturnos_mes": 2, "Festivos_mes": 1, "Hospital": "Hospital Nacional de Niños"},
            {"Código": "HNN-405", "Nombre": "Oscar Armando Peña", "Antigüedad": 4, "Especialidad": "Cirugía", "Turnos_nocturnos_mes": 1, "Festivos_mes": 0, "Hospital": "Hospital Nacional de Niños"},
            {"Código": "HNN-406", "Nombre": "Karla Patricia Bonilla", "Antigüedad": 1, "Especialidad": "UCI", "Turnos_nocturnos_mes": 4, "Festivos_mes": 2, "Hospital": "Hospital Nacional de Niños"}
        ]
        with open(personal_path, 'w', encoding='utf-8') as f:
            json.dump(personal, f, indent=2, ensure_ascii=False)
    
    # Cargar o inicializar datos de festivos
    festivos_path = 'data/festivos.json'
    if os.path.exists(festivos_path):
        with open(festivos_path, 'r', encoding='utf-8') as f:
            festivos = json.load(f)
    else:
        festivos = {
            "01/01/2024": "Año Nuevo",
            "01/05/2024": "Día del Trabajo",
            "06/08/2024": "Fiesta de San Salvador",
            "15/09/2024": "Día de la Independencia",
            "02/11/2024": "Día de los Difuntos",
            "25/12/2024": "Navidad",
            "01/01/2025": "Año Nuevo",
            "01/05/2025": "Día del Trabajo",
            "06/08/2025": "Fiesta de San Salvador",
            "15/09/2025": "Día de la Independencia",
            "02/11/2025": "Día de los Difuntos",
            "25/12/2025": "Navidad"
        }
        with open(festivos_path, 'w', encoding='utf-8') as f:
            json.dump(festivos, f, indent=2, ensure_ascii=False)
    
    return hospitales, departamentos, personal, festivos

def guardar_personal(personal):
    """Guarda los datos del personal en el archivo JSON"""
    with open('data/personal.json', 'w', encoding='utf-8') as f:
        json.dump(personal, f, indent=2, ensure_ascii=False)

def guardar_festivos(festivos):
    """Guarda los datos de festivos en el archivo JSON"""
    with open('data/festivos.json', 'w', encoding='utf-8') as f:
        json.dump(festivos, f, indent=2, ensure_ascii=False)

# --- FUNCIÓN PRINCIPAL PARA ASIGNAR TURNOS ---
def asignar_turnos(personal, dias_a_generar=14, hospital=None):
    if dias_a_generar > 30:
        dias_a_generar = 30
        st.warning("⚠️ El sistema solo permite generar hasta 30 días de turnos")
    
    turnos = []
    fecha_actual = datetime.now()
    
    # Filtrar personal por hospital si se especifica
    personal_filtrado = [p for p in personal if not hospital or p["Hospital"] == hospital]
    
    for dia in range(dias_a_generar):
        fecha = fecha_actual + timedelta(days=dia)
        fecha_str = fecha.strftime("%d/%m/%Y")
        es_festivo = fecha_str in festivos
        
        # Ordenar por prioridad (antigüedad, turnos nocturnos, festivos)
        personal_ordenado = sorted(
            personal_filtrado,
            key=lambda x: (-x["Antigüedad"], x["Turnos_nocturnos_mes"], x["Festivos_mes"])
        )
        
        asignaciones = {"Mañana (7:00-15:00)": None, "Tarde (15:00-23:00)": None, "Noche (23:00-7:00)": None}
        disponibles = personal_ordenado.copy()
        
        for turno in ["Noche (23:00-7:00)", "Tarde (15:00-23:00)", "Mañana (7:00-15:00)"]:
            for persona in disponibles:
                # Reglas de asignación
                if "Noche" in turno and persona["Turnos_nocturnos_mes"] >= 6:
                    continue
                
                # Evitar turnos consecutivos
                if dia > 0:
                    turno_anterior = turnos[-1]
                    if any(turno_anterior[t] == persona["Nombre"] and t == turno for t in turno_anterior):
                        continue
                
                # Descanso post-noche
                if "Mañana" in turno and dia > 0 and turnos[-1]["Noche (23:00-7:00)"] == persona["Nombre"]:
                    continue
                
                # Asignar turno
                asignaciones[turno] = f"{persona['Código']} - {persona['Nombre']}"
                if "Noche" in turno:
                    persona["Turnos_nocturnos_mes"] += 1
                if es_festivo:
                    persona["Festivos_mes"] += 1
                disponibles.remove(persona)
                break
        
        turnos.append({
            "Fecha": fecha_str,
            "Día": fecha.strftime("%A"),
            "Festivo": "✓ " + festivos.get(fecha_str, "") if es_festivo else "",
            "Especialidad Requerida": "Cirugía" if dia % 3 == 0 else "General",
            **asignaciones
        })
    
    return pd.DataFrame(turnos)

# --- CARGAR DATOS ---
hospitales, departamentos, personal, festivos = cargar_datos()

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1 class='header'>Sistema de Gestión de Turnos Hospitalarios</h1>", unsafe_allow_html=True)
st.markdown("**Ministerio de Salud - Gobierno de El Salvador**")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.markdown("### 🔧 Panel de Control")
    hospital_seleccionado = st.selectbox("Seleccionar Hospital:", ["Todos"] + hospitales)
    dias_a_generar = st.slider("Días a generar:", 7, 30, 14)
    especialidad_filtro = st.selectbox("Filtrar por especialidad:", ["Todas"] + departamentos)
    
    st.markdown("---")
    if st.button("🔄 Reiniciar Contadores"):
        for p in personal:
            p["Turnos_nocturnos_mes"] = 0
            p["Festivos_mes"] = 0
        guardar_personal(personal)
        st.markdown('<div class="success-box">Contadores reiniciados exitosamente!</div>', unsafe_allow_html=True)
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Estadísticas Rápidas")
    st.metric("Personal Disponible", len([p for p in personal if hospital_seleccionado == "Todos" or p["Hospital"] == hospital_seleccionado]))
    st.metric("Turnos Nocturnos Promedio", round(np.mean([p["Turnos_nocturnos_mes"] for p in personal]), 1))
    
    st.markdown("---")
    st.markdown("### 🛠 Administración de Datos")
    
    if st.button("✏️ Editar Personal"):
        st.session_state.editar_personal = True
    
    if st.button("📅 Editar Festivos"):
        st.session_state.editar_festivos = True

# --- EDITOR DE PERSONAL ---
if st.session_state.get('editar_personal', False):
    with st.expander("📝 Editor de Personal", expanded=True):
        st.markdown('<div class="warning-box">⚠️ Edita con cuidado. Los cambios se guardarán permanentemente.</div>', unsafe_allow_html=True)
        
        # Convertir a DataFrame para edición
        df_personal = pd.DataFrame(personal)
        edited_personal = st.data_editor(
            df_personal,
            num_rows="dynamic",
            use_container_width=True,
            key="personal_editor"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Guardar Cambios", key="guardar_personal"):
                try:
                    # Convertir a lista de diccionarios
                    personal_actualizado = edited_personal.to_dict('records')
                    
                    # Validar datos
                    errores = []
                    campos_requeridos = ["Código", "Nombre", "Antigüedad", "Especialidad", "Turnos_nocturnos_mes", "Festivos_mes", "Hospital"]
                    
                    for i, emp in enumerate(personal_actualizado, 1):
                        # Verificar campos requeridos
                        for campo in campos_requeridos:
                            if campo not in emp:
                                errores.append(f"Falta el campo '{campo}' en el registro {i}")
                                continue
                            
                        # Validar tipos de datos
                        if not isinstance(emp["Antigüedad"], int) or emp["Antigüedad"] < 0:
                            errores.append(f"Antigüedad inválida para {emp.get('Nombre', 'empleado')} (debe ser número entero positivo)")
                        
                        if not isinstance(emp["Turnos_nocturnos_mes"], int) or emp["Turnos_nocturnos_mes"] < 0:
                            errores.append(f"Turnos nocturnos inválidos para {emp.get('Nombre', 'empleado')}")
                            
                        if not isinstance(emp["Festivos_mes"], int) or emp["Festivos_mes"] < 0:
                            errores.append(f"Festivos inválidos para {emp.get('Nombre', 'empleado')}")
                    
                    if errores:
                        for error in errores:
                            st.error(error)
                    else:
                        # Actualizar y guardar
                        personal.clear()
                        personal.extend(personal_actualizado)
                        guardar_personal(personal)
                        st.markdown('<div class="success-box">Datos de personal actualizados correctamente!</div>', unsafe_allow_html=True)
                        st.session_state.editar_personal = False
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Error al guardar los cambios: {str(e)}")
        
        with col2:
            if st.button("❌ Cancelar", key="cancelar_personal"):
                st.session_state.editar_personal = False
                st.rerun()

# --- EDITOR DE FESTIVOS ---
if st.session_state.get('editar_festivos', False):
    with st.expander("📅 Editor de Días Festivos", expanded=True):
        st.markdown('<div class="warning-box">⚠️ Edita con cuidado. Los cambios se guardarán permanentemente.</div>', unsafe_allow_html=True)
        
        # Convertir a formato editable
        festivos_list = [{"Fecha": k, "Nombre": v} for k, v in festivos.items()]
        df_festivos = pd.DataFrame(festivos_list)
        edited_festivos = st.data_editor(
            df_festivos,
            num_rows="dynamic",
            use_container_width=True,
            key="festivos_editor"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Guardar Festivos", key="guardar_festivos"):
                try:
                    # Validar y preparar nuevos datos
                    nuevos_festivos = {}
                    errores = []
                    
                    for i, row in edited_festivos.iterrows():
                        fecha = row["Fecha"]
                        nombre = row["Nombre"]
                        
                        # Validar formato de fecha
                        try:
                            datetime.strptime(fecha, "%d/%m/%Y")
                        except ValueError:
                            errores.append(f"Línea {i+1}: Formato de fecha incorrecto '{fecha}'. Use DD/MM/YYYY")
                            continue
                            
                        if not nombre or not nombre.strip():
                            errores.append(f"Línea {i+1}: El nombre del festivo no puede estar vacío")
                            continue
                            
                        nuevos_festivos[fecha] = nombre.strip()
                    
                    if errores:
                        for error in errores:
                            st.error(error)
                    else:
                        # Actualizar y guardar
                        festivos.clear()
                        festivos.update(nuevos_festivos)
                        guardar_festivos(festivos)
                        st.markdown('<div class="success-box">Datos de festivos actualizados correctamente!</div>', unsafe_allow_html=True)
                        st.session_state.editar_festivos = False
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Error al procesar los datos: {str(e)}")
        
        with col2:
            if st.button("❌ Cancelar", key="cancelar_festivos"):
                st.session_state.editar_festivos = False
                st.rerun()

# --- GENERAR TURNOS ---
df_turnos = asignar_turnos(
    personal, 
    dias_a_generar, 
    hospital=None if hospital_seleccionado == "Todos" else hospital_seleccionado
)

# --- FILTRAR RESULTADOS ---
if especialidad_filtro != "Todas":
    personal_especialidad = [f"{p['Código']} - {p['Nombre']}" for p in personal if p["Especialidad"] == especialidad_filtro]
    df_filtrado = df_turnos[
        df_turnos["Mañana (7:00-15:00)"].isin(personal_especialidad) |
        df_turnos["Tarde (15:00-23:00)"].isin(personal_especialidad) |
        df_turnos["Noche (23:00-7:00)"].isin(personal_especialidad)
    ]
else:
    df_filtrado = df_turnos

# --- VISUALIZACIÓN DE RESULTADOS ---
tab1, tab2, tab3 = st.tabs(["📅 Turnos Generados", "📊 Estadísticas", "📋 Resumen"])

with tab1:
    st.markdown(f"### Turnos Generados - {hospital_seleccionado if hospital_seleccionado != 'Todos' else 'Todos los hospitales'}")
    
    # Formatear el DataFrame para mejor visualización
    df_display = df_filtrado.copy()
    df_display["Festivo"] = df_display["Festivo"].apply(lambda x: "✓" if x else "")
    
    st.dataframe(
        df_display.style
        .applymap(lambda x: "background-color: #FFF2CC" if "✓" in str(x) else "", subset=["Festivo"])
        .applymap(lambda x: "background-color: #E6F3FF" if "Noche" in str(x) else "", subset=["Noche (23:00-7:00)"])
        .format({"Festivo": lambda x: "✓ " + festivos.get(x.split("✓ ")[1]) if "✓" in x else ""}),
        height=600,
        use_container_width=True
    )

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Turnos Nocturnos por Personal")
        nocturnos = pd.DataFrame([{
            "Personal": p["Nombre"], 
            "Turnos Nocturnos": p["Turnos_nocturnos_mes"],
            "Límite": 6
        } for p in personal])
        
        st.bar_chart(
            nocturnos.set_index("Personal"),
            color=["#FF6B6B", "#4E79A7"]
        )
    
    with col2:
        st.markdown("#### Distribución por Especialidad")
        especialidades = pd.DataFrame([{
            "Especialidad": p["Especialidad"],
            "Personal": 1
        } for p in personal])
        
        st.bar_chart(
            especialidades.groupby("Especialidad").count(),
            color="#59A14F"
        )

with tab3:
    st.markdown("#### Resumen de Asignaciones")
    
    resumen = pd.DataFrame({
        "Total Turnos": [len(df_turnos)],
        "Turnos Nocturnos": [df_turnos["Noche (23:00-7:00)"].count()],
        "Días Festivos": [df_turnos[df_turnos["Festivo"] != ""].shape[0]],
        "Personal Involucrado": [len(set(
            [x for x in pd.concat([
                df_turnos["Mañana (7:00-15:00)"],
                df_turnos["Tarde (15:00-23:00)"],
                df_turnos["Noche (23:00-7:00)"]
            ]).dropna() if isinstance(x, str)]
        ))]
    }).T
    
    st.table(resumen.style.format("{:.0f}"))

# --- EXPORTACIÓN ---
st.markdown("---")
col_exp1, col_exp2 = st.columns([1, 3])

with col_exp1:
    formato_export = st.selectbox("Formato de exportación:", ["Excel", "CSV", "PDF"])

with col_exp2:
    if formato_export == "Excel":
        if st.button("💾 Exportar a Excel", help="Genera un archivo Excel con los turnos"):
            df_turnos.to_excel("turnos_hospitalarios.xlsx", index=False)
            st.success("Archivo 'turnos_hospitalarios.xlsx' generado correctamente")
    elif formato_export == "CSV":
        if st.button("💾 Exportar a CSV", help="Genera un archivo CSV con los turnos"):
            df_turnos.to_csv("turnos_hospitalarios.csv", index=False)
            st.success("Archivo 'turnos_hospitalarios.csv' generado correctamente")
    else:
        st.warning("Exportación a PDF requiere configuración adicional")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>Sistema desarrollado con fines educativos<br>
    AugvstTTY<br>
    Versión 2.3 - Agosto 2024</p>
</div>
""", unsafe_allow_html=True)
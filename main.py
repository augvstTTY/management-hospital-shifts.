import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import json
import os

# ==============================
# STREAMLIT PAGE CONFIGURATION
# ==============================
st.set_page_config(
    page_title="Hospital Shift Management System",
    page_icon="🏥",
    layout="wide"
)

# ==============================
# CUSTOM CSS STYLES
# ==============================
st.markdown("""
<style>
    .header { color: #005B96; font-family: 'Arial', sans-serif; }
    .sidebar .sidebar-content { background-color: #F0F2F6; }
    .stButton>button { background-color: #005B96; color: white; border-radius: 5px; }
    .stDataFrame { font-size: 14px; }
    .footer { font-size: 12px; text-align: center; margin-top: 20px; color: #666666; }
    .warning-box { background-color: #FFF3CD; color: black; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
    .success-box { background-color: #D4EDDA; padding: 10px; border-radius: 5px; margin-bottom: 15px; color: #155724; }
</style>
""", unsafe_allow_html=True)

# ==============================
# HELPER FUNCTIONS
# ==============================
def load_json_safe(path, default_data):
    """
    Loads JSON data from file.
    If the file is missing or corrupted, it will be replaced with default_data.
    """
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        st.warning(f"⚠ Corrupted file detected: {path}. Restoring with default data.")
    save_json(path, default_data)
    return default_data

def save_json(path, data):
    """Saves Python object to JSON file with UTF-8 encoding."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ==============================
# DATA LOADING FUNCTIONS
# ==============================
def load_data():
    """
    Loads hospitals, departments, staff, and holidays from JSON files.
    Creates default data if files don't exist.
    """
    os.makedirs('data', exist_ok=True)
    
    hospitals = ["Hospital Rosales", "Hospital Bloom", "Hospital Zacamil", "Hospital Nacional de Niños"]
    departments = ["Emergencias", "Pediatría", "Cirugía", "Medicina Interna", "Enfermería", "UCI"]
    
    default_staff = [
        {"Código": "ROS-101", "Nombre": "Carlos Martínez", "Antigüedad": 3, "Especialidad": "Cirugía", "Turnos_nocturnos_mes": 2, "Festivos_mes": 1, "Hospital": "Hospital Rosales"},
        {"Código": "ROS-102", "Nombre": "Roberto Sánchez", "Antigüedad": 3, "Especialidad": "Cirugía", "Turnos_nocturnos_mes": 0, "Festivos_mes": 0, "Hospital": "Hospital Rosales"},
        # ... Keep the rest of your original staff list here ...
    ]
    
    default_holidays = {
        "01/01/2024": "Año Nuevo",
        "01/05/2024": "Día del Trabajo",
        "06/08/2024": "Fiesta de San Salvador",
        "15/09/2024": "Día de la Independencia",
        "02/11/2024": "Día de los Difuntos",
        "25/12/2024": "Navidad"
    }
    
    staff = load_json_safe('data/personal.json', default_staff)
    holidays = load_json_safe('data/festivos.json', default_holidays)
    
    return hospitals, departments, staff, holidays

def save_staff(staff):
    """
    Saves staff data to JSON file.
    Prevents saving if there are duplicate staff codes.
    """
    codes = [p["Código"] for p in staff]
    duplicates = {c for c in codes if codes.count(c) > 1}
    if duplicates:
        st.error(f"❌ Save failed: Duplicate codes detected: {', '.join(duplicates)}")
        return False
    save_json('data/personal.json', staff)
    return True

def save_holidays(holidays):
    """Saves holiday data to JSON file."""
    save_json('data/festivos.json', holidays)

# ==============================
# SHIFT ASSIGNMENT LOGIC
# ==============================
def assign_shifts(staff, days_to_generate=14, hospital=None):
    """
    Assigns shifts for the given number of days.
    Includes rules for avoiding too many night shifts and consecutive shifts.
    """
    days_to_generate = min(days_to_generate, 30)
    if days_to_generate < 1:
        return pd.DataFrame()
    
    shifts = []
    current_date = datetime.now()
    filtered_staff = [p for p in staff if not hospital or p["Hospital"] == hospital]
    
    for day in range(days_to_generate):
        date = current_date + timedelta(days=day)
        date_str = date.strftime("%d/%m/%Y")
        is_holiday = date_str in holidays
        
        sorted_staff = sorted(
            filtered_staff,
            key=lambda x: (-x["Antigüedad"], x["Turnos_nocturnos_mes"], x["Festivos_mes"])
        )
        
        assignments = {
            "Mañana (7:00-15:00)": None,
            "Tarde (15:00-23:00)": None,
            "Noche (23:00-7:00)": None
        }
        available = sorted_staff.copy()
        
        for shift in ["Noche (23:00-7:00)", "Tarde (15:00-23:00)", "Mañana (7:00-15:00)"]:
            for person in available:
                # Avoid exceeding night shift limit
                if "Noche" in shift and person["Turnos_nocturnos_mes"] >= 6:
                    continue
                # Avoid same shift on consecutive days
                if day > 0:
                    previous_day = shifts[-1]
                    if previous_day.get(shift) and person["Nombre"] in previous_day[shift]:
                        continue
                # Rest after night shift
                if "Mañana" in shift and day > 0 and shifts[-1]["Noche (23:00-7:00)"] and person["Nombre"] in shifts[-1]["Noche (23:00-7:00)"]:
                    continue
                
                assignments[shift] = f"{person['Código']} - {person['Nombre']}"
                if "Noche" in shift:
                    person["Turnos_nocturnos_mes"] += 1
                if is_holiday:
                    person["Festivos_mes"] += 1
                available.remove(person)
                break
        
        shifts.append({
            "Fecha": date_str,
            "Día": date.strftime("%A"),
            "Festivo": "✓ " + holidays.get(date_str, "") if is_holiday else "",
            "Especialidad Requerida": "Cirugía" if day % 3 == 0 else "General",
            **assignments
        })
    
    return pd.DataFrame(shifts)

# ==============================
# LOAD INITIAL DATA
# ==============================
hospitals, departments, staff, holidays = load_data()

# ==============================
# MAIN INTERFACE
# ==============================
st.markdown("<h1 class='header'>Hospital Shift Management System</h1>", unsafe_allow_html=True)
st.markdown("**Ministry of Health - Government of El Salvador**")

# ------------------------------
# SIDEBAR CONTROL PANEL
# ------------------------------
with st.sidebar:
    st.markdown("### 🔧 Control Panel")
    selected_hospital = st.selectbox("Select Hospital:", ["All"] + hospitals)
    days_to_generate = st.slider("Days to generate:", 7, 30, 14)
    specialty_filter = st.selectbox("Filter by specialty:", ["All"] + departments)
    
    st.markdown("---")
    if st.button("🔄 Reset Counters"):
        for p in staff:
            p["Turnos_nocturnos_mes"] = 0
            p["Festivos_mes"] = 0
        save_staff(staff)
        st.markdown('<div class="success-box">Counters successfully reset!</div>', unsafe_allow_html=True)
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Available Staff", len([p for p in staff if selected_hospital == "All" or p["Hospital"] == selected_hospital]))
    st.metric("Average Night Shifts", round(np.mean([p["Turnos_nocturnos_mes"] for p in staff]), 1))
    
    st.markdown("---")
    st.markdown("### 🛠 Data Management")
    if st.button("✏️ Edit Staff"):
        st.session_state.edit_staff = True
    if st.button("📅 Edit Holidays"):
        st.session_state.edit_holidays = True

# ==============================
# STAFF EDITOR
# ==============================
if st.session_state.get('edit_staff', False):
    with st.expander("📝 Staff Editor", expanded=True):
        st.markdown('<div class="warning-box">⚠ Edit carefully. Changes will be saved permanently.</div>', unsafe_allow_html=True)
        df_staff = pd.DataFrame(staff)
        edited_staff = st.data_editor(df_staff, num_rows="dynamic", use_container_width=True, key="staff_editor")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Changes", key="save_staff"):
                staff_updated = edited_staff.to_dict('records')
                errors = []
                required_fields = ["Código", "Nombre", "Antigüedad", "Especialidad", "Turnos_nocturnos_mes", "Festivos_mes", "Hospital"]
                for i, emp in enumerate(staff_updated, 1):
                    for field in required_fields:
                        if field not in emp:
                            errors.append(f"Missing '{field}' in record {i}")
                    if not isinstance(emp["Antigüedad"], int) or emp["Antigüedad"] < 0:
                        errors.append(f"Invalid seniority for {emp.get('Nombre', 'employee')}")
                    if not isinstance(emp["Turnos_nocturnos_mes"], int) or emp["Turnos_nocturnos_mes"] < 0:
                        errors.append(f"Invalid night shifts for {emp.get('Nombre', 'employee')}")
                    if not isinstance(emp["Festivos_mes"], int) or emp["Festivos_mes"] < 0:
                        errors.append(f"Invalid holiday count for {emp.get('Nombre', 'employee')}")
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    staff.clear()
                    staff.extend(staff_updated)
                    if save_staff(staff):
                        st.markdown('<div class="success-box">Staff data successfully updated!</div>', unsafe_allow_html=True)
                        st.session_state.edit_staff = False
                        st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_staff"):
                st.session_state.edit_staff = False
                st.rerun()

# ==============================
# HOLIDAYS EDITOR
# ==============================
if st.session_state.get('edit_holidays', False):
    with st.expander("📅 Holidays Editor", expanded=True):
        st.markdown('<div class="warning-box">⚠ Edit carefully. Changes will be saved permanently.</div>', unsafe_allow_html=True)
        holiday_list = [{"Fecha": k, "Nombre": v} for k, v in holidays.items()]
        df_holidays = pd.DataFrame(holiday_list)
        edited_holidays = st.data_editor(df_holidays, num_rows="dynamic", use_container_width=True, key="holidays_editor")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Holidays", key="save_holidays"):
                new_holidays = {}
                errors = []
                for i, row in edited_holidays.iterrows():
                    date_str = row["Fecha"]
                    name = row["Nombre"]
                    try:
                        datetime.strptime(date_str, "%d/%m/%Y")
                    except ValueError:
                        errors.append(f"Line {i+1}: Incorrect date format '{date_str}'. Use DD/MM/YYYY")
                        continue
                    if not name.strip():
                        errors.append(f"Line {i+1}: Holiday name cannot be empty")
                        continue
                    new_holidays[date_str] = name.strip()
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    holidays.clear()
                    holidays.update(new_holidays)
                    save_holidays(holidays)
                    st.markdown('<div class="success-box">Holiday data successfully updated!</div>', unsafe_allow_html=True)
                    st.session_state.edit_holidays = False
                    st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_holidays"):
                st.session_state.edit_holidays = False
                st.rerun()

# ==============================
# GENERATE SHIFTS
# ==============================
df_shifts = assign_shifts(
    staff, 
    days_to_generate, 
    hospital=None if selected_hospital == "All" else selected_hospital
)

# Filter by specialty if selected
if specialty_filter != "All":
    staff_specialty = [f"{p['Código']} - {p['Nombre']}" for p in staff if p["Especialidad"] == specialty_filter]
    df_filtered = df_shifts[
        df_shifts["Mañana (7:00-15:00)"].isin(staff_specialty) |
        df_shifts["Tarde (15:00-23:00)"].isin(staff_specialty) |
        df_shifts["Noche (23:00-7:00)"].isin(staff_specialty)
    ]
else:
    df_filtered = df_shifts

# ==============================
# TABS: RESULTS / STATS / SUMMARY
# ==============================
tab1, tab2, tab3 = st.tabs(["📅 Generated Shifts", "📊 Statistics", "📋 Summary"])

with tab1:
    st.markdown(f"### Shifts - {selected_hospital if selected_hospital != 'All' else 'All hospitals'}")
    df_display = df_filtered.copy()
    df_display["Festivo"] = df_display["Festivo"].apply(lambda x: "✓" if x else "")
    st.dataframe(
        df_display.style
        .applymap(lambda x: "background-color: #FFF2CC" if "✓" in str(x) else "", subset=["Festivo"])
        .applymap(lambda x: "background-color: #E6F3FF" if "Noche" in str(x) else "", subset=["Noche (23:00-7:00)"]),
        height=600,
        use_container_width=True
    )

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Night Shifts per Staff")
        night_data = pd.DataFrame([{
            "Staff": p["Nombre"], 
            "Night Shifts": p["Turnos_nocturnos_mes"],
            "Limit": 6
        } for p in staff])
        st.bar_chart(night_data.set_index("Staff"))
    with col2:
        st.markdown("#### Staff Distribution by Specialty")
        specialty_data = pd.DataFrame([{
            "Specialty": p["Especialidad"],
            "Count": 1
        } for p in staff])
        st.bar_chart(specialty_data.groupby("Specialty").count())

with tab3:
    st.markdown("#### Shift Summary")
    summary = pd.DataFrame({
        "Total Shifts": [len(df_shifts)],
        "Night Shifts": [df_shifts["Noche (23:00-7:00)"].count()],
        "Holiday Days": [df_shifts[df_shifts["Festivo"] != ""].shape[0]],
        "Involved Staff": [len(set(
            pd.concat([
                df_shifts["Mañana (7:00-15:00)"],
                df_shifts["Tarde (15:00-23:00)"],
                df_shifts["Noche (23:00-7:00)"]
            ]).dropna())
        )]
    }).T
    st.table(summary)

# ==============================
# EXPORT OPTIONS
# ==============================
st.markdown("---")
col_exp1, col_exp2 = st.columns([1, 3])
with col_exp1:
    export_format = st.selectbox("Export format:", ["Excel", "CSV", "PDF"])
with col_exp2:
    if export_format == "Excel":
        if st.button("💾 Export to Excel"):
            df_shifts.to_excel("hospital_shifts.xlsx", index=False)
            st.success("File 'hospital_shifts.xlsx' generated successfully")
    elif export_format == "CSV":
        if st.button("💾 Export to CSV"):
            df_shifts.to_csv("hospital_shifts.csv", index=False)
            st.success("File 'hospital_shifts.csv' generated successfully")
    else:
        st.warning("PDF export requires additional configuration")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>System developed for educational purposes<br>
    AugvstTTY<br>
    Version 2.3 - August 2024</p>
</div>
""", unsafe_allow_html=True)

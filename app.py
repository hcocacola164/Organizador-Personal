import datetime
from datetime import date
import streamlit as st
from supabase import create_client

# ================= CONFIGURACIÓN DE SUPABASE =================
SUPABASE_URL = "https://ruevjfgysrdariugzebm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ1ZXZqZmd5c3JkYXJpdWd6ZWJtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NjU0NDMsImV4cCI6MjEwOTE0MTQ0M30.5KtT8V0AmWwdvY335_zDwwkWIBSiMHEshXALkASo7dA"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= CONFIGURACIÓN DE LA PÁGINA =================
st.set_page_config(
    page_title="JARVIS Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: linear-gradient(135deg, #030712 0%, #0d1b2a 100%);
        color: #f0f4f8;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, .metric-container {
        font-family: 'Orbitron', sans-serif !important;
    }
    h1 {
        color: #00f2fe !important;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
        font-weight: 800;
        letter-spacing: 2px;
    }
    /* Estilo para los botones principales grandes tipo tarjeta */
    .stButton>button {
        background: linear-gradient(135deg, #0d1b2a, #1b263b);
        color: #00f2fe;
        font-weight: 700;
        border: 1px solid rgba(0, 242, 254, 0.4);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        width: 100%;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        font-family: 'Orbitron', sans-serif;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00f2fe, #4facfe);
        color: #030712;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.6);
        border-color: #00f2fe;
        transform: translateY(-2px);
    }
    .task-card {
        background: rgba(13, 27, 42, 0.85);
        border: 1px solid rgba(0, 242, 254, 0.25);
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    div[data-testid="metric-container"] {
        background: rgba(0, 242, 254, 0.05);
        border: 1px solid rgba(0, 242, 254, 0.2);
        padding: 12px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Control de la sección activa
if "active_module" not in st.session_state:
    st.session_state["active_module"] = "SUHAILA"

col_title, col_clock = st.columns([3, 1])
with col_title:
    st.markdown("<h1>⚡ JARVIS COMMAND CENTER</h1>", unsafe_allow_html=True)
with col_clock:
    current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.markdown(f"<p style='text-align: right; color: #00f2fe; font-family: Orbitron; font-size: 1.1rem;'>{current_time}</p>", unsafe_allow_html=True)

st.markdown("---")

# Tarjetas / Botones de Navegación Superiores
m1, m2, m3 = st.columns(3)
with m1:
    if st.button("👩‍👧 MÓDULO SUHAILA"):
        st.session_state["active_module"] = "SUHAILA"
with m2:
    if st.button("🏠 MÓDULO CASA"):
        st.session_state["active_module"] = "CASA"
with m3:
    if st.button("⏰ RECORDATORIOS"):
        st.session_state["active_module"] = "RECORDATORIOS"

st.markdown("<br>", unsafe_allow_html=True)

def fetch_data(table_name):
    response = supabase.table(table_name).select("*").order("id", desc=True).execute()
    return response.data

def add_task(table_name, data_dict):
    supabase.table(table_name).insert(data_dict).execute()

def update_task(table_name, task_id, update_dict):
    supabase.table(table_name).update(update_dict).eq("id", task_id).execute()

def delete_task(table_name, task_id):
    supabase.table(table_name).delete().eq("id", task_id).execute()

def render_kpis(data):
    total = len(data)
    completadas = sum(1 for x in data if x.get("completed", False))
    pendientes = total - completadas
    porcentaje = int((completadas / total * 100) if total > 0 else 0)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📊 Total Tareas", total)
    k2.metric("⏳ Pendientes", pendientes)
    k3.metric("✅ Completadas", completadas)
    k4.metric("📈 Progreso", f"{porcentaje}%")
    st.markdown("<br>", unsafe_allow_html=True)

# ================= MÓDULO SUHAILA =================
if st.session_state["active_module"] == "SUHAILA":
    st.subheader("// MÓDULO DE GESTIÓN: SUHAILA")
    data_suh = fetch_data("suhaila")
    render_kpis(data_suh)

    with st.expander("➕ Añadir Nueva Tarea / Actividad", expanded=False):
        with st.form("form_suhaila", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cat = st.text_input("Categoría (ej: Baile, Cole)")
                start_d = st.date_input("Fecha Inicio", value=date.today())
            with col2:
                task = st.text_input("Descripción de la Tarea")
                end_d = st.date_input("Fecha Fin", value=date.today())

            submitted = st.form_submit_button("REGISTRAR EN SISTEMA")
            if submitted and task:
                add_task("suhaila", {
                    "id": int(datetime.datetime.now().timestamp() * 1000),
                    "category": cat or "General",
                    "task": task,
                    "start_date": str(start_d),
                    "end_date": str(end_d),
                    "completed": False
                })
                st.rerun()

    f_col1, _ = st.columns([2, 2])
    with f_col1:
        filtro_estado = st.selectbox("Filtrar vista", ["Todas", "Pendientes", "Completadas"], key="f_suh")

    st.markdown("### Registros Activos")
    for row in data_suh:
        if filtro_estado == "Pendientes" and row["completed"]:
            continue
        if filtro_estado == "Completadas" and not row["completed"]:
            continue

        edit_key = f"editing_suh_{row['id']}"
        
        with st.container():
            st.markdown('<div class="task-card">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.08, 0.65, 0.13, 0.14])
            with c1:
                is_done = st.checkbox("", value=row["completed"], key=f"chk_suh_{row['id']}")
                if is_done != row["completed"]:
                    update_task("suhaila", row["id"], {"completed": is_done})
                    st.rerun()
            with c2:
                style = "text-decoration: line-through; opacity: 0.4;" if row["completed"] else ""
                st.markdown(
                    f"<span style='background:rgba(0,242,254,0.15); color:#00f2fe; padding:3px 8px; border-radius:6px; font-size:0.75rem; font-weight:600;'>{row['category']}</span><br>"
                    f"<span style='{style} font-weight:600; font-size:1.05rem; display:inline-block; margin-top:5px;'>{row['task']}</span><br>"
                    f"<span style='font-size:0.8rem; color:#94a3b8;'>🗓️ {row['start_date']} ➔ {row['end_date']}</span>",
                    unsafe_allow_html=True
                )
            with c3:
                if st.button("✏️ Editar", key=f"edit_suh_btn_{row['id']}"):
                    st.session_state[edit_key] = not st.session_state.get(edit_key, False)
            with c4:
                if st.button("🗑️ Borrar", key=f"del_suh_{row['id']}"):
                    delete_task("suhaila", row["id"])
                    st.rerun()

            if st.session_state.get(edit_key, False):
                with st.form(key=f"form_edit_suh_{row['id']}"):
                    new_task_txt = st.text_input("Modificar Tarea", value=row["task"])
                    new_cat_txt = st.text_input("Modificar Categoría", value=row["category"])
                    if st.form_submit_button("Guardar Cambios"):
                        update_task("suhaila", row["id"], {"task": new_task_txt, "category": new_cat_txt})
                        st.session_state[edit_key] = False
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ================= MÓDULO CASA =================
elif st.session_state["active_module"] == "CASA":
    st.subheader("// MÓDULO DE GESTIÓN: CASA")
    data_casa = fetch_data("casa")
    render_kpis(data_casa)

    with st.expander("➕ Añadir Nueva Tarea Doméstica", expanded=False):
        with st.form("form_casa", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cat_c = st.text_input("Categoría (ej: Limpieza)", key="cat_c")
                start_c = st.date_input("Fecha Inicio", value=date.today(), key="start_c")
            with col2:
                task_c = st.text_input("Descripción de la Tarea", key="task_c")
                end_c = st.date_input("Fecha Fin", value=date.today(), key="end_c")

            submitted_c = st.form_submit_button("REGISTRAR EN SISTEMA")
            if submitted_c and task_c:
                add_task("casa", {
                    "id": int(datetime.datetime.now().timestamp() * 1000),
                    "category": cat_c or "General",
                    "task": task_c,
                    "start_date": str(start_c),
                    "end_date": str(end_c),
                    "completed": False
                })
                st.rerun()

    f_col1_c, _ = st.columns([2, 2])
    with f_col1_c:
        filtro_estado_c = st.selectbox("Filtrar vista", ["Todas", "Pendientes", "Completadas"], key="f_cas")

    st.markdown("### Registros Activos")
    for row in data_casa:
        if filtro_estado_c == "Pendientes" and row["completed"]:
            continue
        if filtro_estado_c == "Completadas" and not row["completed"]:
            continue

        edit_key_c = f"editing_cas_{row['id']}"

        with st.container():
            st.markdown('<div class="task-card">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.08, 0.65, 0.13, 0.14])
            with c1:
                is_done_c = st.checkbox("", value=row["completed"], key=f"chk_cas_{row['id']}")
                if is_done_c != row["completed"]:
                    update_task("casa", row["id"], {"completed": is_done_c})
                    st.rerun()
            with c2:
                style = "text-decoration: line-through; opacity: 0.4;" if row["completed"] else ""
                st.markdown(
                    f"<span style='background:rgba(0,242,254,0.15); color:#00f2fe; padding:3px 8px; border-radius:6px; font-size:0.75rem; font-weight:600;'>{row['category']}</span><br>"
                    f"<span style='{style} font-weight:600; font-size:1.05rem; display:inline-block; margin-top:5px;'>{row['task']}</span><br>"
                    f"<span style='font-size:0.8rem; color:#94a3b8;'>🗓️ {row['start_date']} ➔ {row['end_date']}</span>",
                    unsafe_allow_html=True
                )
            with c3:
                if st.button("✏️ Editar", key=f"edit_cas_btn_{row['id']}"):
                    st.session_state[edit_key_c] = not st.session_state.get(edit_key_c, False)
            with c4:
                if st.button("🗑️ Borrar", key=f"del_cas_{row['id']}"):
                    delete_task("casa", row["id"])
                    st.rerun()

            if st.session_state.get(edit_key_c, False):
                with st.form(key=f"form_edit_cas_{row['id']}"):
                    new_task_txt_c = st.text_input("Modificar Tarea", value=row["task"])
                    new_cat_txt_c = st.text_input("Modificar Categoría", value=row["category"])
                    if st.form_submit_button("Guardar Cambios"):
                        update_task("casa", row["id"], {"task": new_task_txt_c, "category": new_cat_txt_c})
                        st.session_state[edit_key_c] = False
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ================= MÓDULO RECORDATORIOS =================
elif st.session_state["active_module"] == "RECORDATORIOS":
    st.subheader("// MÓDULO DE ALARMAS Y RECORDATORIOS")
    data_rec = fetch_data("recordatorios")

    with st.expander("➕ Programar Nuevo Evento / Alarma", expanded=False):
        with st.form("form_rec", clear_on_submit=True):
            r_title = st.text_input("Título del Recordatorio")
            r_datetime = st.datetime_input("Fecha y Hora del Evento", value=datetime.datetime.now())

            submitted_r = st.form_submit_button("PROGRAMAR ALARMA")
            if submitted_r and r_title:
                add_task("recordatorios", {
                    "id": int(datetime.datetime.now().timestamp() * 1000),
                    "title": r_title,
                    "datetime": r_datetime.isoformat(),
                    "notified_7d": False,
                    "notified_1d": False,
                    "last_daily_notice": ""
                })
                st.rerun()

    st.markdown("### Alarmas Programadas")
    for row in data_rec:
        with st.container():
            st.markdown('<div class="task-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                dt_formatted = datetime.datetime.fromisoformat(row["datetime"]).strftime("%d/%m/%Y %H:%M") if row["datetime"] else ""
                st.markdown(
                    f"<span style='font-weight:600; font-size:1.1rem; color:#f0f4f8;'>{row['title']}</span><br>"
                    f"<span style='font-size:0.9rem; color:#00f2fe; font-family:Orbitron;'>⏰ {dt_formatted}</span>",
                    unsafe_allow_html=True
                )
            with c2:
                if st.button("🗑️ Borrar", key=f"del_rec_{row['id']}"):
                    delete_task("recordatorios", row["id"])
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
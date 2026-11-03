from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import streamlit as st
from supabase import create_client

# ================= CONFIGURACIÓN DE SUPABASE =================
SUPABASE_URL = "https://ruevjfgysrdariugzebm.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInI1cCI5..."
)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= CONFIGURACIÓN DE LA PÁGINA =================
st.set_page_config(
    page_title="MyHome Command Center",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ================= ESTILOS CSS & FUENTE ORBITRON =================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f19;
        color: #e2e8f0;
    }

    h1, h2, h3, .brand-title {
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #38bdf8;
        border: 1px solid #38bdf8;
        font-family: 'Orbitron', sans-serif;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background: #38bdf8;
        color: #0f172a;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ================= HORA LOCAL ESPAÑA =================
ahora_espana = datetime.now(ZoneInfo("Europe/Madrid"))
fecha_hoy_str = ahora_espana.strftime("%Y-%m-%d")


# ================= FUNCIÓN CALLMEBOT CON USUARIO =================
def enviar_aviso_callmebot(mensaje, usuario, apikey):
  url = "https://api.callmebot.com/telegram/get.php"
  params = {"phone": usuario, "text": mensaje, "apikey": apikey}
  try:
    response = requests.get(url, params=params)
    return response.status_code == 200
  except Exception:
    return False


# ================= VENTANA EMERGENTE (POP-UP) PARA HOY =================
@st.dialog("🚨 MyHome: Alertas del Día (Suhaila & Casa)")
def mostrar_modal_hoy(tareas_hoy):
  st.write(
      "Aquí tienes los pendientes programados para hoy en **Suhaila** y"
      " **Casa**:"
  )
  for tarea in tareas_hoy:
    st.markdown(
        f"🔹 **[{tarea.get('category')}]** {tarea.get('title')} — ⏰"
        f" {tarea.get('datetime')}"
    )

  if st.button("Entrar a MyHome"):
    st.rerun()


def verificar_alertas_diarias():
  try:
    response = (
        supabase.table("tasks")
        .select("*")
        .in_("category", ["Suhaila", "Casa"])
        .execute()
    )
    tareas = response.data if response.data else []
    tareas_hoy = [
        t for t in tareas if t.get("datetime", "").startswith(fecha_hoy_str)
    ]

    if "modal_visto" not in st.session_state:
      if tareas_hoy:
        mostrar_modal_hoy(tareas_hoy)
      st.session_state.modal_visto = True
  except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")


# Ejecutar verificación de pop-up al cargar
verificar_alertas_diarias()

# ================= INTERFAZ PRINCIPAL =================
st.markdown(
    "<h1 style='text-align: center; color: #38bdf8;'>🏠 MYHOME COMMAND"
    " CENTER</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align: center; color: #94a3b8;'>Hora local actual:"
    f" {ahora_espana.strftime('%d/%m/%Y %H:%M')}</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Pestañas de navegación
tab1, tab2, tab3, tab4 = st.tabs(
    ["📋 Suhaila", "🏠 Casa", "🌐 General", "⏰ Alarmas y Recordatorios"]
)


def gestionar_seccion(categoria):
  st.subheader(f"Gestión de {categoria}")

  with st.form(key=f"form_{categoria}"):
    titulo = st.text_input("Nuevo evento / tarea / recordatorio")
    fecha_hora = st.text_input(
        "Fecha y Hora (Ej: 2026-11-03 17:15)",
        value=ahora_espana.strftime("%Y-%m-%d %H:%M"),
    )
    submitted = st.form_submit_button("Programar Evento")

    if submitted and titulo:
      try:
        supabase.table("tasks").insert({
            "title": titulo,
            "category": categoria,
            "datetime": fecha_hora,
            "status": "pending",
        }).execute()
        st.success(f"¡Guardado en {categoria}!")
        st.rerun()
      except Exception as e:
        st.error(f"Error al guardar: {e}")

  st.markdown("### Listado Activo")
  try:
    res = (
        supabase.table("tasks")
        .select("*")
        .eq("category", categoria)
        .order("datetime")
        .execute()
    )
    items = res.data if res.data else []

    if not items:
      st.info(f"No hay registros en {categoria}.")
    for row in items:
      col1, col2 = st.columns([4, 1])
      with col1:
        st.markdown(
            f"📌 **{row['title']}**<br>⏰ `{row['datetime']}`",
            unsafe_allow_html=True,
        )
      with col2:
        if st.button("Borrar", key=f"del_{row['id']}"):
          supabase.table("tasks").delete().eq("id", row["id"]).execute()
          st.rerun()
      st.markdown("---")
  except Exception as e:
    st.error(f"Error al cargar datos: {e}")


with tab1:
  gestionar_seccion("Suhaila")

with tab2:
  gestionar_seccion("Casa")

with tab3:
  gestionar_seccion("General")

with tab4:
  st.subheader("⏰ Alarmas, Recordatorios y Telegram")

  # Configurado con tu usuario y tu API key
  tel_input = "@Jossee93"
  apikey_input = "14.93"

  st.markdown("### Alarmas Program
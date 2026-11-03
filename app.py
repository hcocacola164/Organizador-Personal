from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import streamlit as st
from supabase import create_client

# ================= CONFIGURACIÓN DE SUPABASE =================
SUPABASE_URL = "https://ruevjfgysrdariugzebm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ1ZXZqZmd5c3JkYXJpdWd6ZWJtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NjU0NDMsImV4cCI6MjEwOTE0MTQ0M30.5KtT8V0AmWwdvY335_zDwwkWIBSiMHEshXALkASo7dA"
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


# ================= FUNCIÓN CALLMEBOT =================
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

# =
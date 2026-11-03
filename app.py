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

# Comprobación de alertas del día de forma segura
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
  if tareas_hoy:
    st.warning(
        f"🚨 **Aviso diario:** Tienes {len(tareas_hoy)} tarea(s) programada(s)"
        " para hoy en Suhaila o Casa."
    )
except Exception:
  pass

# Pestañas de navegación
tab1, tab2, tab3, tab4 = st.tabs(
    ["📋 Suhaila", "🏠 Casa", "🌐 General", "⏰ Alarmas y Recordatorios"]
)


def gestionar_seccion(categoria):
  st.subheader(f"Gestión de {categoria}")

  with st.form(key=f"form_{categoria}"):
    titulo = st.text_input("Nuevo evento / tarea / recordatorio")
    fecha
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


# ================= FUNCIÓN CALLMEBOT OFICIAL =================
def enviar_aviso_callmebot(mensaje, usuario, apikey):
  url = "https://api.callmebot.com/text.php"
  params = {"user": usuario, "text": mensaje, "apikey": apikey}
  try:
    response = requests.get(url, params=params)
    if response.status_code == 200:
      return True, "OK"
    else:
      return False, f"HTTP {response.status_code}: {response.text}"
  except Exception as e:
    return False, str(e)


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

    # Selector tipo calendario y rueda de hora estilo alarma
    col_f, col_h = st.columns(2)
    with col_f:
      f_sel = st.date_input("Fecha del evento", value=ahora_espana.date())
    with col_h:
      h_sel = st.time_input("Hora del evento", value=ahora_espana.time())

    submitted = st.form_submit_button("Programar Evento")

    if submitted and titulo:
      fecha_hora_str = f"{f_sel} {h_sel.strftime('%H:%M')}"
      try:
        supabase.table("tasks").insert({
            "title": titulo,
            "category": categoria,
            "datetime": fecha_hora_str,
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

      # Bloque desplegable de edición para cada tarea
      with st.expander(f"✏️ Editar '{row['title']}'"):
        nuevo_titulo = st.text_input(
            "Modificar Título", value=row["title"], key=f"t_edit_{row['id']}"
        )
        nueva_cat = st.selectbox(
            "Modificar Categoría",
            ["Suhaila", "Casa", "General"],
            index=["Suhaila", "Casa", "General"].index(
                row.get("category", "General")
            )
            if row.get("category") in ["Suhaila", "Casa", "General"]
            else 2,
            key=f"c_edit_{row['id']}",
        )

        try:
          dt_parse = datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M")
        except:
          dt_parse = ahora_espana

        col_ef, col_eh = st.columns(2)
        with col_ef:
          nf_sel = st.date_input(
              "Nueva Fecha", value=dt_parse.date(), key=f"f_edit_{row['id']}"
          )
        with col_eh:
          nh_sel = st.time_input(
              "Nueva Hora", value=dt_parse.time(), key=f"h_edit_{row['id']}"
          )

        if st.button("💾 Guardar Cambios", key=f"save_edit_{row['id']}"):
          nuevo_dt_str = f"{nf_sel} {nh_sel.strftime('%H:%M')}"
          try:
            supabase.table("tasks").update({
                "title": nuevo_titulo,
                "category": nueva_cat,
                "datetime": nuevo_dt_str,
            }).eq("id", row["id"]).execute()
            st.success("¡Tarea actualizada con éxito!")
            st.rerun()
          except Exception as e:
            st.error(f"Error al actualizar: {e}")

      st.markdown("---")
  except Exception as e:
    st.error(f"Error al cargar datos: {e}")


# Renderizar contenido dentro de cada pestaña
with tab1:
  gestionar_seccion("Suhaila")

with tab2:
  gestionar_seccion("Casa")

with tab3:
  gestionar_seccion("General")

with tab4:
  st.subheader("⏰ Alarmas, Recordatorios y Telegram")

  tel_input = "@Jossee93"
  apikey_input = "14.93"

  st.markdown("### Alarmas Programadas")
  try:
    res = supabase.table("tasks").select("*").execute()
    todas = res.data if res.data else []

    if not todas:
      st.info("No hay alarmas programadas.")
    for row in todas:
      col1, col2, col3 = st.columns([3, 1, 1])
      with col1:
        st.markdown(
            f"🔔 **[{row.get('category')}] {row.get('title')}**<br>⏰"
            f" `{row.get('datetime')}`",
            unsafe_allow_html=True,
        )
      with col2:
        if st.button("📲 Enviar Telegram", key=f"tg_{row['id']}"):
          texto = (
              f"🚨 *RECORDATORIO MYHOME*\n• [{row.get('category')}]"
              f" {row.get('title')}\n⏰ Fecha: {row.get('datetime')}"
          )
          exito, detalle = enviar_aviso_callmebot(
              texto, tel_input, apikey_input
          )
          if exito:
            st.success("¡Enviado!")
          else:
            st.error(f"Fallo al enviar: {detalle}")
      with col3:
        if st.button("Borrar", key=f"del_alarm_{row['id']}"):
          supabase.table("tasks").delete().eq("id", row["id"]).execute()
          st.rerun()
      st.markdown("---")
  except Exception as e:
    st.error(f"Error al cargar alarmas: {e}")
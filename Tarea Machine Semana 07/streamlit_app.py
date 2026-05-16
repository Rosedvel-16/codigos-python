from datetime import datetime

import streamlit as st

# Modulos de dominio que entregan las salidas del motor de reglas por escenario.
import ejercicio1_academico as academico
import ejercicio2_biblioteca as biblioteca
import ejercicio3_logistica as logistica

# Configuracion global de la pagina Streamlit.
st.set_page_config(page_title="Sistemas Expertos", page_icon="✨", layout="wide")

# CSS global para definir el tema visual y estilos de componentes.
st.markdown(
    """
    <style>
    :root {
        --ink: #0f172a;
        --muted: #6b7280;
        --accent: #ff6b4a;
        --accent-2: #1fbba6;
        --accent-3: #f6c065;
        --card: #ffffff;
        --shadow: rgba(15, 23, 42, 0.12);
    }
    .stApp {
        background: radial-gradient(1200px 600px at 5% -10%, #ffe1d6, transparent 70%),
                    radial-gradient(900px 500px at 95% 0%, #dff7f3, transparent 60%),
                    radial-gradient(800px 500px at 50% 100%, #fff2d5, transparent 65%),
                    linear-gradient(180deg, #f7f8fb 0%, #f2f5f9 100%);
        color: var(--ink);
    }
    .hero {
        padding: 22px 28px;
        border-radius: 18px;
        background: linear-gradient(135deg, #0f172a 0%, #1f2a44 55%, #ff6b4a 180%);
        color: #ffffff;
        box-shadow: 0 18px 40px var(--shadow);
    }
    .hero h1 {
        font-size: 2.2rem;
        margin-bottom: 6px;
    }
    .hero p {
        color: #d7dbe5;
        margin: 0;
    }
    .pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.16);
        font-size: 0.85rem;
        margin-right: 8px;
    }
    .card {
        background: var(--card);
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 10px 24px var(--shadow);
        height: 100%;
    }
    .card h3 {
        margin-top: 0;
        color: var(--ink);
        font-size: 1.1rem;
    }
    .tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        background: #f0f3f7;
        color: var(--muted);
        font-size: 0.75rem;
        margin-left: 6px;
    }
    .footer-note {
        color: var(--muted);
        font-size: 0.85rem;
        margin-top: 12px;
    }
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, #ff9b7b 100%);
        border: none;
        color: #ffffff;
        font-weight: 600;
        padding: 0.55rem 1.1rem;
        border-radius: 12px;
        box-shadow: 0 10px 24px rgba(255, 122, 89, 0.25);
    }
        [data-testid="stMetric"] {
            background: #ffffff;
            padding: 14px 16px;
            border-radius: 14px;
            box-shadow: 0 10px 24px var(--shadow);
            border: 1px solid rgba(15, 23, 42, 0.06);
        }
        [data-testid="stMetric"] > div {
            color: var(--muted);
        }
        [data-testid="stMetricValue"] {
            color: var(--ink);
            font-size: 1.4rem;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            color: var(--muted);
            font-weight: 600;
        }
    .stButton > button:hover {
        transform: translateY(-1px);
        transition: transform 120ms ease;
    }
    .soft-panel {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.6);
        padding: 12px 16px;
        border-radius: 14px;
        box-shadow: 0 10px 24px var(--shadow);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Helper seguro para contar elementos sin fallar con listas vacias.
def total_count(items):
    return len(items) if items else 0


# Renderiza una tarjeta con titulo y lista de items separados por coma.
def render_list(title, items, emoji=""):
    pretty = ", ".join(items) if items else "(sin resultados)"
    st.markdown(
        f"""
        <div class="card">
            <h3>{emoji} {title}</h3>
            <p>{pretty}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Renderiza las consultas booleanas como tarjetas con distintivos SI/NO.
def render_consultas(consultas):
    cols = st.columns(3)
    items = list(consultas.items())
    for index, (label, value) in enumerate(items):
        badge = "SI" if value else "NO"
        color = "#0f766e" if value else "#b42318"
        with cols[index % 3]:
            st.markdown(
                f"""
                <div class="card">
                    <h3>{label}</h3>
                    <span class="tag" style="color: {color}; font-weight: 700;">{badge}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# Layout completo para el sistema experto academico.
def render_academico(show_consultas, show_reglas, show_kpis):
    data = academico.get_context()
    # Bloque hero con contexto para la seccion.
    st.markdown(
        """
        <div class="hero">
            <span class="pill">Sistema Experto</span>
            <span class="pill">Academico</span>
            <h1>Evaluacion academica inteligente</h1>
            <p>Reglas logicas para determinar aprobaciones, becas y seguimiento.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    # Fila de KPIs con metricas resumidas.
    if show_kpis:
        kpi = st.columns(4)
        kpi[0].metric("Aprueban", total_count(data["aprueba"]))
        kpi[1].metric("Desaprueban", total_count(data["desaprueba"]))
        kpi[2].metric("Postulan a beca", total_count(data["puede_postular_beca"]))
        kpi[3].metric("Seguimiento", total_count(data["requiere_seguimiento"]))

    # Primera grilla de listas de resultados.
    grid = st.columns(4)
    with grid[0]:
        render_list("Aprueban", data["aprueba"], "✅")
    with grid[1]:
        render_list("Desaprueban", data["desaprueba"], "❌")
    with grid[2]:
        render_list("Habilitados para cierre", data["habilitado_cierre"], "🎓")
    with grid[3]:
        render_list("Observacion por inasistencia", data["observacion_inasistencia"], "⚠️")

    # Segunda grilla de listas de resultados.
    grid = st.columns(4)
    with grid[0]:
        render_list("Postulacion a beca", data["puede_postular_beca"], "💰")
    with grid[1]:
        render_list("Reconocimiento academico", data["reconocimiento_academico"], "🏅")
    with grid[2]:
        render_list("Requiere seguimiento", data["requiere_seguimiento"], "🔍")
    with grid[3]:
        render_list("Alta prioridad de beca", data["alta_prioridad_beca"], "⭐")

    # Seccion opcional de consultas.
    if show_consultas:
        st.subheader("Consultas especificas")
        render_consultas(data["consultas"])

    # Visualizacion opcional de reglas para transparencia.
    if show_reglas:
        with st.expander("Reglas aplicadas"):
            st.code("\n".join(academico.RULES), language="text")


# Layout completo para el sistema experto de biblioteca.
def render_biblioteca(show_consultas, show_reglas, show_kpis):
    data = biblioteca.get_context()
    # Bloque hero con contexto para la seccion.
    st.markdown(
        """
        <div class="hero">
            <span class="pill">Sistema Experto</span>
            <span class="pill">Biblioteca</span>
            <h1>Reglas para prestamo y reservas</h1>
            <p>Evaluacion de multas, suspension y prioridades.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    # Fila de KPIs con metricas resumidas.
    if show_kpis:
        kpi = st.columns(4)
        kpi[0].metric("Con multa", total_count(data["tiene_multa"]))
        kpi[1].metric("Suspendidos", total_count(data["servicio_suspendido"]))
        kpi[2].metric("Renovaciones", total_count(data["puede_renovar"]))
        kpi[3].metric("Habilitados", total_count(data["usuario_habilitado"]))

    # Primera grilla de listas de resultados.
    grid = st.columns(4)
    with grid[0]:
        render_list("Usuarios con multa", data["tiene_multa"], "⚠️")
    with grid[1]:
        render_list("Servicio suspendido", data["servicio_suspendido"], "🚫")
    with grid[2]:
        render_list("Pueden renovar", data["puede_renovar"], "🔄")
    with grid[3]:
        render_list("Prioridad de prestamo", data["prioridad_prestamo"], "🎖️")

    # Segunda grilla de listas de resultados.
    grid = st.columns(4)
    with grid[0]:
        render_list("Reserva prioritaria", data["reserva_prioritaria"], "📌")
    with grid[1]:
        render_list("Reserva especial", data["reserva_especial"], "🔑")
    with grid[2]:
        render_list("Maxima prioridad", data["maxima_prioridad"], "⭐")
    with grid[3]:
        render_list("Usuarios habilitados", data["usuario_habilitado"], "✅")

    # Seccion opcional de consultas.
    if show_consultas:
        st.subheader("Consultas especificas")
        render_consultas(data["consultas"])

    # Visualizacion opcional de reglas para transparencia.
    if show_reglas:
        with st.expander("Reglas aplicadas"):
            st.code("\n".join(biblioteca.RULES), language="text")


# Layout completo para el sistema experto de logistica.
def render_logistica(show_consultas, show_reglas, show_kpis):
    data = logistica.get_context()
    # Bloque hero con contexto para la seccion.
    st.markdown(
        """
        <div class="hero">
            <span class="pill">Sistema Experto</span>
            <span class="pill">Logistica</span>
            <h1>Logistica de entregas con reglas</h1>
            <p>Prioriza pedidos y determina envios inmediatos.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    # Fila de KPIs con metricas resumidas.
    if show_kpis:
        kpi = st.columns(4)
        kpi[0].metric("Programables", total_count(data["puede_programarse"]))
        kpi[1].metric("Prioritarios", total_count(data["atencion_prioritaria"]))
        kpi[2].metric("Envio hoy", total_count(data["puede_enviarse_hoy"]))
        kpi[3].metric("Max. prioridad", total_count(data["maxima_prioridad_logistica"]))

    # Primera grilla de listas de resultados.
    grid = st.columns(4)
    with grid[0]:
        render_list("Puede programarse", data["puede_programarse"], "📦")
    with grid[1]:
        render_list("Atencion prioritaria", data["atencion_prioritaria"], "🚨")
    with grid[2]:
        render_list("Embalaje especial", data["embalaje_especial"], "📦")
    with grid[3]:
        render_list("Confirmacion adicional", data["confirmacion_adicional"], "❗")

    # Segunda grilla de listas de resultados.
    grid = st.columns(4)
    with grid[0]:
        render_list("Entrega inmediata", data["entrega_inmediata"], "⚡")
    with grid[1]:
        render_list("Puede enviarse hoy", data["puede_enviarse_hoy"], "✈️")
    with grid[2]:
        render_list("Maxima prioridad", data["maxima_prioridad_logistica"], "🔴")
    with grid[3]:
        render_list("Asignacion ejecutiva", data["asignacion_ejecutiva"], "👑")

    # Seccion opcional de consultas.
    if show_consultas:
        st.subheader("Consultas especificas")
        render_consultas(data["consultas"])

    # Visualizacion opcional de reglas para transparencia.
    if show_reglas:
        with st.expander("Reglas aplicadas"):
            st.code("\n".join(logistica.RULES), language="text")


# Sidebar: selector de ejercicios y controles globales.
st.sidebar.title("Panel de ejercicios")
st.sidebar.write("Selecciona el sistema experto que quieres visualizar.")
selector = st.sidebar.radio(
    "Ejercicio",
    ["Academico", "Biblioteca", "Logistica"],
    index=0,
)

st.sidebar.subheader("Controles")
show_kpis = st.sidebar.toggle("Mostrar indicadores", value=True)
show_consultas = st.sidebar.toggle("Mostrar consultas", value=True)
show_reglas = st.sidebar.toggle("Mostrar reglas", value=False)

# Recarga manual para recalcular datos y mostrar hora.
if st.sidebar.button("Recalcular datos"):
    st.session_state["last_refresh"] = datetime.now().strftime("%H:%M:%S")
    st.toast("Datos recalculados")

if "last_refresh" in st.session_state:
    st.sidebar.caption(f"Ultima recarga: {st.session_state['last_refresh']}")

# Panel auxiliar en el sidebar.
st.sidebar.markdown(
    """
    <div class="soft-panel">
        <strong>Tip visual</strong><br />
        Alterna indicadores y reglas para una vista mas limpia.
    </div>
    """,
    unsafe_allow_html=True,
)

# Enruta al sistema experto seleccionado.
if selector == "Academico":
    render_academico(show_consultas, show_reglas, show_kpis)
elif selector == "Biblioteca":
    render_biblioteca(show_consultas, show_reglas, show_kpis)
else:
    render_logistica(show_consultas, show_reglas, show_kpis)

# Pie de pagina con sugerencia para ejecutar la app localmente.
st.markdown(
    "<div class='footer-note'>Tip: ejecuta con <strong>streamlit run streamlit_app.py</strong></div>",
    unsafe_allow_html=True,
)
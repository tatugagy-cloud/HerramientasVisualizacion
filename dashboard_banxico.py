# Tablero del SIE de Banxico, con token
# Herramientas de Visualización · IDIA221 · Unidad III
#
#     pip install -r requirements.txt
#     streamlit run dashboard_banxico.py
#
# EL TOKEN NO VA EN ESTE ARCHIVO.
# En tu equipo: crea la carpeta .streamlit y dentro un archivo secrets.toml
# con una sola línea:
#     banxico_token = "pega-aqui-tu-token"
# Al publicar: pega esa misma línea en la sección de secretos de la app.
# El archivo secrets.toml nunca se sube al repositorio.

import os
from datetime import date, datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import streamlit as st

# ─── Paleta del curso ──────────────────────────────────────────────────
GRIS = "#B9C3D1"
AZUL = "#1C4C9A"
ROJO = "#B2182B"
AZUL_POS = "#2166AC"
CUALI = ["#E69F00", "#56B4E9", "#009E73", "#0072B2"]
sns.set_theme(style="whitegrid")

SIE = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

st.set_page_config(page_title="Tablero del SIE", layout="wide")


# ─── Token y datos ─────────────────────────────────────────────────────
def obtener_token():
    try:
        return st.secrets["banxico_token"]
    except Exception:
        return os.environ.get("BANXICO_TOKEN", "")


@st.cache_data(ttl=3600, show_spinner="Consultando Banxico...")
def cargar_serie(id_serie, inicio, fin, token):
    url = f"{SIE}/{id_serie}/datos/{inicio}/{fin}"
    r = requests.get(url, headers={"Bmx-Token": token}, timeout=30)
    r.raise_for_status()
    datos = r.json()["bmx"]["series"][0].get("datos", [])
    df = pd.DataFrame(datos)
    if df.empty:
        return df
    df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["dato"].str.replace(",", ""), errors="coerce")
    return df[["fecha", "valor"]].dropna().sort_values("fecha").reset_index(drop=True)


# ─── Interfaz ──────────────────────────────────────────────────────────
st.title("Tablero del SIE de Banxico")

token = obtener_token()
if not token:
    st.error("Falta el token. Agrégalo en .streamlit/secrets.toml como banxico_token.")
    st.stop()

SERIES = {
    "Tipo de cambio FIX (SF43718)": "SF43718",
    "Tipo de cambio para solventar obligaciones (SF60653)": "SF60653",
    "TIIE 28 días (SF43783)": "SF43783",
}

st.sidebar.header("Filtros")
nombre = st.sidebar.selectbox("Serie", list(SERIES.keys()))
inicio = st.sidebar.date_input("Desde", date(2024, 1, 1))
fin = st.sidebar.date_input("Hasta", date.today())
ventana = st.sidebar.slider("Ventana de la media móvil (días)", 3, 60, 7)

if inicio >= fin:
    st.warning("La fecha inicial debe ser anterior a la final.")
    st.stop()

try:
    df = cargar_serie(SERIES[nombre], inicio.isoformat(), fin.isoformat(), token)
except requests.HTTPError as e:
    st.error(f"Banxico rechazó la consulta (revisa tu token): {e}")
    st.stop()
except Exception as e:
    st.error(f"No se pudo consultar la API: {e}")
    st.stop()

if df.empty:
    st.info("No hay datos para ese rango de fechas.")
    st.stop()

df["variacion"] = df["valor"].pct_change() * 100
df["media_movil"] = df["valor"].rolling(ventana).mean()

# ─── Indicadores ───────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Último valor", f"{df['valor'].iloc[-1]:.4f}")
c2.metric("Variación vs. anterior", f"{df['variacion'].iloc[-1]:.2f}%")
c3.metric("Mínimo", f"{df['valor'].min():.4f}")
c4.metric("Máximo", f"{df['valor'].max():.4f}")

# ─── Gráfica 1: serie histórica ────────────────────────────────────────
st.subheader("Serie histórica")
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(df["fecha"], df["valor"], color=AZUL, linewidth=1.8)
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Valor")
st.pyplot(fig1)
plt.close(fig1)

# ─── Gráfica 2: variación diaria ───────────────────────────────────────
st.subheader("Variación diaria (%)")
colores = [AZUL_POS if v >= 0 else ROJO for v in df["variacion"].fillna(0)]
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.bar(df["fecha"], df["variacion"], color=colores, width=1.0)
ax2.axhline(0, color=GRIS, linewidth=1)
ax2.set_xlabel("Fecha")
ax2.set_ylabel("Cambio %")
st.pyplot(fig2)
plt.close(fig2)

# ─── Gráfica 3 (NUEVA): media móvil ────────────────────────────────────
st.subheader(f"Tendencia con media móvil de {ventana} días")
fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.plot(df["fecha"], df["valor"], color=GRIS, label="Valor diario")
ax3.plot(df["fecha"], df["media_movil"], color=CUALI[0], linewidth=2.2,
         label=f"Media móvil {ventana} días")
ax3.set_xlabel("Fecha")
ax3.set_ylabel("Valor")
ax3.legend()
st.pyplot(fig3)
plt.close(fig3)

# ─── Datos ─────────────────────────────────────────────────────────────
with st.expander("Ver datos"):
    st.dataframe(df, use_container_width=True)

# Gráfica QUITADA: histograma de distribución del valor (sns.histplot).
# Motivo: no muestra la evo
import os
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# =====================================================
# CONFIGURACION GENERAL
# =====================================================

st.set_page_config(
    page_title="Panel Financiero | Banxico",
    page_icon="📊",
    layout="wide"
)

SIE = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

AZUL = "#2563EB"
FONDO = "#0E172A"
TEXTO = "#E5E7EB"

st.markdown("""
<style>
.stApp {
    background-color: #0E172A;
    color: #E5E7EB;
}
[data-testid="stMetric"] {
    background-color: #18253B;
    border: 1px solid #263B5B;
    padding: 18px;
    border-radius: 12px;
}
[data-testid="stMetricLabel"] {
    color: #A9B9D0;
}
h1, h2, h3 {
    color: #F8FAFC;
}
section[data-testid="stSidebar"] {
    background-color: #142039;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# CONEXION CON BANXICO
# =====================================================

def obtener_token():
    try:
        return st.secrets["banxico_token"]
    except Exception:
        return os.environ.get("BANXICO_TOKEN", "")


@st.cache_data(ttl=3600)
def cargar_serie(id_serie, inicio, fin, token):

    url = f"{SIE}/{id_serie}/datos/{inicio}/{fin}"

    respuesta = requests.get(
        url,
        headers={"Bmx-Token": token},
        timeout=30
    )

    respuesta.raise_for_status()

    datos = respuesta.json()["bmx"]["series"][0].get("datos", [])

    df = pd.DataFrame(datos)

    if df.empty:
        return df

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        format="%d/%m/%Y"
    )

    df["valor"] = pd.to_numeric(
        df["dato"].str.replace(",", ""),
        errors="coerce"
    )

    return (
        df[["fecha", "valor"]]
        .dropna()
        .sort_values("fecha")
        .reset_index(drop=True)
    )


# =====================================================
# ENCABEZADO
# =====================================================

st.title("📊 PANEL DE INDICADORES FINANCIEROS")

st.markdown(
    "### Banco de México | Sistema de Información Económica"
)

st.caption(
    "Dashboard interactivo para el análisis de indicadores financieros."
)

st.divider()


# =====================================================
# SERIES DISPONIBLES
# =====================================================

SERIES = {
    "Tipo de cambio FIX": "SF43718",
    "Tipo de cambio para obligaciones": "SF60653",
    "TIIE a 28 días": "SF43783"
}


# =====================================================
# FILTROS LATERALES
# =====================================================

st.sidebar.title("⚙️ Panel de control")

nombre = st.sidebar.selectbox(
    "Selecciona un indicador",
    list(SERIES.keys())
)

inicio = st.sidebar.date_input(
    "Fecha inicial",
    date(2024, 1, 1)
)

fin = st.sidebar.date_input(
    "Fecha final",
    date.today()
)

ventana = st.sidebar.slider(
    "Periodo de media móvil",
    3,
    60,
    7
)

comparar = st.sidebar.checkbox(
    "Mostrar comparación de indicadores"
)

st.sidebar.divider()

st.sidebar.caption(
    "Fuente de información: Banco de México (Banxico)"
)


# =====================================================
# VALIDACIONES
# =====================================================

if inicio >= fin:
    st.error("La fecha inicial debe ser anterior a la fecha final.")
    st.stop()

token = obtener_token()

if not token:
    st.error(
        "No se encontró el token de Banxico. "
        "Configúralo en .streamlit/secrets.toml."
    )
    st.stop()


# =====================================================
# CONSULTA PRINCIPAL
# =====================================================

try:

    with st.spinner("Consultando información de Banxico..."):

        df = cargar_serie(
            SERIES[nombre],
            inicio.isoformat(),
            fin.isoformat(),
            token
        )

except requests.HTTPError as e:

    st.error(f"Error HTTP al consultar Banxico: {e}")
    st.stop()

except requests.RequestException as e:

    st.error(f"Error de conexión: {e}")
    st.stop()

except Exception as e:

    st.error(f"Error al procesar los datos: {e}")
    st.stop()


if df.empty:
    st.warning("No se encontraron datos para las fechas seleccionadas.")
    st.stop()


# =====================================================
# PROCESAMIENTO DE DATOS
# =====================================================

df["variacion"] = df["valor"].pct_change() * 100

df["media_movil"] = (
    df["valor"].rolling(ventana).mean()
)


ultimo = df["valor"].iloc[-1]

anterior = (
    df["valor"].iloc[-2]
    if len(df) > 1
    else ultimo
)

variacion = (
    ((ultimo - anterior) / anterior) * 100
    if anterior != 0
    else 0
)

promedio = df["valor"].mean()
minimo = df["valor"].min()
maximo = df["valor"].max()


# =====================================================
# TARJETAS KPI
# =====================================================

st.subheader("Indicadores principales")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Último valor",
    f"{ultimo:,.4f}",
    f"{variacion:+.2f}%"
)

c2.metric(
    "Promedio",
    f"{promedio:,.4f}"
)

c3.metric(
    "Valor mínimo",
    f"{minimo:,.4f}"
)

c4.metric(
    "Valor máximo",
    f"{maximo:,.4f}"
)

st.divider()


# =====================================================
# GRAFICA HISTORICA
# =====================================================

st.subheader("📈 Evolución histórica")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df["fecha"],
        y=df["valor"],
        mode="lines",
        name="Valor del indicador",
        line=dict(color=AZUL, width=2)
    )
)

fig.add_trace(
    go.Scatter(
        x=df["fecha"],
        y=df["media_movil"],
        mode="lines",
        name="Media móvil",
        line=dict(color="#F59E0B", width=2)
    )
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor=FONDO,
    plot_bgcolor=FONDO,
    xaxis_title="Fecha",
    yaxis_title="Valor",
    hovermode="x unified",
    height=430,
    legend=dict(orientation="h", y=1.12)
)

st.plotly_chart(fig, use_container_width=True)


# =====================================================
# VARIACION DEL INDICADOR
# =====================================================

st.subheader("📉 Variación porcentual")

fig2 = px.bar(
    df,
    x="fecha",
    y="variacion",
    color="variacion",
    color_continuous_scale="RdYlGn",
    labels={
        "fecha": "Fecha",
        "variacion": "Variación (%)"
    }
)

fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor=FONDO,
    plot_bgcolor=FONDO,
    height=350
)

st.plotly_chart(fig2, use_container_width=True)


# =====================================================
# COMPARACION DE INDICADORES
# =====================================================

if comparar:

    st.divider()

    st.subheader("📊 Comparación de indicadores")

    seleccion = st.multiselect(
        "Selecciona las series que deseas comparar",
        list(SERIES.keys()),
        default=[nombre]
    )

    if seleccion:

        fig3 = go.Figure()

        for serie in seleccion:

            try:

                datos = cargar_serie(
                    SERIES[serie],
                    inicio.isoformat(),
                    fin.isoformat(),
                    token
                )

                if not datos.empty:

                    fig3.add_trace(
                        go.Scatter(
                            x=datos["fecha"],
                            y=datos["valor"],
                            mode="lines",
                            name=serie
                        )
                    )

            except requests.RequestException as e:

                st.warning(f"No se pudo cargar {serie}: {e}")

        fig3.update_layout(
            template="plotly_dark",
            paper_bgcolor=FONDO,
            plot_bgcolor=FONDO,
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig3, use_container_width=True)


# =====================================================
# TABLA DE DATOS
# =====================================================

st.divider()

st.subheader("📋 Datos consultados")

st.dataframe(
    df.sort_values("fecha", ascending=False),
    use_container_width=True,
    hide_index=True
)

csv = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "⬇️ Descargar datos CSV",
    data=csv,
    file_name="indicadores_banxico.csv",
    mime="text/csv"
)


# =====================================================
# PIE DE PAGINA
# =====================================================

st.divider()

st.caption(
    "Proyecto académico | Ingeniería en Datos e Inteligencia Artificial"
)

st.caption(
    "Datos obtenidos mediante la API del Sistema de Información Económica de Banxico."
)
st.caption(
    "Análisis de la evolución en el tiempo, que es lo importante en una serie."
)
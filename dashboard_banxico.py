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
# Motivo: no muestra la evolución en el tiempo, que es lo importante en una serie.
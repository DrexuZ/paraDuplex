import streamlit as st
import pandas as pd
import plotly.express as px

# Título
st.set_page_config(page_title="Dashboard de Campañas", layout="wide")
st.title("📊 Dashboard de Campañas Publicitarias")

# Cargar datos


@st.cache_data
def cargar_datos():
    return pd.read_csv("datos.csv", parse_dates=["fecha"])


df = cargar_datos()

# Filtros
campañas = st.sidebar.multiselect(
    "Selecciona campaña", options=df["campaña"].unique(), default=df["campaña"].unique())
fecha_min = df["fecha"].min()
fecha_max = df["fecha"].max()
rango_fecha = st.sidebar.date_input("Rango de fechas", [fecha_min, fecha_max])

# Filtrar
df_filtrado = df[
    (df["campaña"].isin(campañas)) &
    (df["fecha"] >= pd.to_datetime(rango_fecha[0])) &
    (df["fecha"] <= pd.to_datetime(rango_fecha[1]))
]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Alcance total", f"{df_filtrado['alcance'].sum():,}")
col2.metric("Clics totales", f"{df_filtrado['clicks'].sum():,}")
col3.metric("Costo Promedio", f"${df_filtrado['costo'].mean():.2f}")
col4.metric("Inversión total", f"${df_filtrado['total_gastado'].sum():.2f}")

# Gráficos
st.subheader("📈 Evolución diaria")
fig = px.line(df_filtrado, x="fecha", y="clicks",
              color="campaña", title="Clics por día")
st.plotly_chart(fig, use_container_width=True)

fig2 = px.bar(df_filtrado, x="fecha", y="total_gastado",
              color="campaña", title="Gasto diario")
st.plotly_chart(fig2, use_container_width=True)

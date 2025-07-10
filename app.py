"""
Dashboard para análisis de campañas publicitarias de Meta Ads

Módulo principal que carga datos de CSV y muestra métricas clave
con visualizaciones interactivas usando Streamlit.
"""

# Standard library imports
import os
from datetime import datetime

# Third-party imports
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def cargar_datos():
    """Carga y procesa los datos de Meta Ads desde CSV"""
    try:
        data = pd.read_csv(
            "Andres-Del-Castillo-Campanas-9-jun.-2025-8-jul.-2025.csv",
            parse_dates=["Inicio del informe", "Fin del informe", "Fin"],
            encoding='utf-8'
        )

        # Renombrar columnas y calcular métricas
        df_clean = data.rename(columns={
            "Nombre de la campaña": "campana",
            "Importe gastado (BOB)": "gasto",
            "Impresiones": "impresiones",
            "Alcance": "alcance",
            "Resultados": "resultados",
            "Coste por resultados": "costo_por_resultado"
        })
        
        # Calcular métricas adicionales
        df_clean["CTR"] = (df_clean["resultados"] / df_clean["impresiones"]) * 100  # CTR en %
        df_clean["CPM"] = (df_clean["gasto"] / df_clean["impresiones"]) * 1000  # Costo por mil impresiones
        
        return df_clean

    except (FileNotFoundError, pd.errors.EmptyDataError, KeyError, pd.errors.ParserError) as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

# Carga de datos
df = cargar_datos()

if df.empty:
    st.warning("No se encontraron datos. Verifica el archivo CSV.")
    st.stop()

# Sidebar con filtros
with st.sidebar:
    st.header("🔍 Filtros")

    # Filtro por campaña
    campanas_seleccionadas = st.multiselect(
        "Seleccionar campañas",
        options=df["campana"].unique(),
        default=df["campana"].unique(),
        format_func=lambda x: x.split(":")[-1].strip()  # Muestra solo parte descriptiva
    )

    # Filtro por fecha
    col1, col2 = st.columns(2)
    with col1:
        fecha_min = st.date_input(
            "Fecha inicial",
            value=df["Inicio del informe"].min().to_pydatetime(),
            min_value=df["Inicio del informe"].min().to_pydatetime(),
            max_value=df["Fin del informe"].max().to_pydatetime()
        )
    with col2:
        fecha_max = st.date_input(
            "Fecha final",
            value=df["Fin del informe"].max().to_pydatetime(),
            min_value=df["Inicio del informe"].min().to_pydatetime(),
            max_value=df["Fin del informe"].max().to_pydatetime()
        )

# Aplicar filtros
df_filtrado = df[
    (df["campana"].isin(campanas_seleccionadas)) &
    (df["Inicio del informe"] >= pd.to_datetime(fecha_min)) &
    (df["Fin del informe"] <= pd.to_datetime(fecha_max))
]

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

# KPIs
st.header("📈 Métricas Clave")
cols = st.columns(4)
cols[0].metric("Total Gastado (BOB)", f"{df_filtrado['gasto'].sum():,.2f}",
              help="Suma total del presupuesto gastado en las campañas seleccionadas")
cols[1].metric("Resultados Totales", f"{df_filtrado['resultados'].sum():,}",
              help="Conversiones totales (inicios de conversación)")
cols[2].metric("CTR Promedio", f"{df_filtrado['CTR'].mean():.2f}%",
              help="Tasa de clics promedio (Clics/Impresiones)")
cols[3].metric("CPM Promedio", f"{df_filtrado['CPM'].mean():.2f} BOB",
              help="Costo por mil impresiones promedio")

# Gráficos
tab1, tab2, tab3 = st.tabs(["📊 Eficiencia", "📌 Comparación", "📅 Evolución"])

with tab1:
    st.subheader("Eficiencia de Campañas")
    fig = px.scatter(
        df_filtrado,
        x="gasto",
        y="resultados",
        color="campana",
        size="impresiones",
        hover_data=["costo_por_resultado", "CTR", "CPM"],
        title="Resultados vs Inversión",
        labels={
            "gasto": "Gasto Total (BOB)",
            "resultados": "Conversiones",
            "campana": "Campaña"
        }
    )
    fig.update_layout(showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Comparación entre Campañas")
    fig = px.bar(
        df_filtrado.sort_values("resultados", ascending=False),
        x="campana",
        y=["resultados", "gasto"],
        barmode="group",
        title="Rendimiento por Campaña",
        labels={"value": "Cantidad", "variable": "Métrica"},
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Evolución Temporal")
    fig = go.Figure()
    
    color_sequence = px.colors.qualitative.Plotly
    
    for i, campana in enumerate(df_filtrado["campana"].unique()):
        temp_df = df_filtrado[df_filtrado["campana"] == campana]
        fig.add_trace(go.Scatter(
            x=temp_df["Inicio del informe"],
            y=temp_df["resultados"],
            name=campana.split(":")[-1].strip(),
            mode="lines+markers",
            line=dict(color=color_sequence[i], width=2),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Evolución de Conversiones",
        xaxis_title="Fecha",
        yaxis_title="Conversiones",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# Tabla detallada
st.header("📋 Datos Detallados")
st.dataframe(
    df_filtrado[[
        "campana", "Inicio del informe", "Fin del informe",
        "gasto", "resultados", "impresiones", "alcance",
        "CTR", "CPM", "costo_por_resultado"
    ]].sort_values("gasto", ascending=False),
    use_container_width=True,
    height=400,
    column_config={
        "gasto": st.column_config.NumberColumn(format="%.2f BOB"),
        "CTR": st.column_config.NumberColumn(format="%.2f%%"),
        "CPM": st.column_config.NumberColumn(format="%.2f BOB")
    }
)

# Información adicional
with st.expander("ℹ️ Acerca de este dashboard"):
    st.write("""
    **Fuente de datos:** Exportación directa desde Meta Ads Manager  
    **Métricas clave:**
    - **CTR (Click-Through Rate):** Porcentaje de impresiones que resultaron en clics
    - **CPM (Costo por Mil Impresiones):** Costo por cada 1,000 impresiones
    - **Costo por resultado:** Gasto promedio por conversión obtenida
    """)

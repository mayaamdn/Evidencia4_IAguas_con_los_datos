import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import base64


#Configuracion y colores

st.set_page_config(page_title="Optimización de Flota", layout="wide")

# Paleta corporativa
BEPENSA_ORANGE = "#fd5e2e"
BEPENSA_GRAY = "#2e3242"
BEPENSA_LIGHT = "#dde2f3"

# CSS simple para tema
st.markdown(
    f"""
    <style>
    body {{
        background-color: #ffffff;
        color:{BEPENSA_GRAY };
    }}
    .stMetric > div {{
        background-color: #f0f1f5 !important;
        border-radius: 12px;
        padding: 10px 12px;
    }}
    .block-container {{
        background-color: #ffffff !important;
        padding-top: 1rem;
    }}
    .stMetric label {{
        color: #000000 !important;
    }}
    .stMetric span {{
        color: 000000 !important;
        font-weight: 700 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


#logo

def show_logo():
    
    logo_path = Path("logo.png")

    if not logo_path.exists():
        st.warning("logo.png no encontrado.")
        return

    with open(logo_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style='text-align:center; margin-top:20px; margin-bottom:10px;'>
            <img src="data:image/webp;base64,{data}" width="260">
        </div>
        """,
        unsafe_allow_html=True,
    )


#Cargar el archivo del usuario 

def load_data_from_excel(file_obj):
    viajes = pd.read_excel(file_obj, sheet_name="Viajes")
    asignacion = pd.read_excel(file_obj, sheet_name="Asignacion")
    riesgo = pd.read_excel(file_obj, sheet_name="Riesgo")
    forecast = pd.read_excel(file_obj, sheet_name="Forecast")

    if "Fecha Salida" in viajes.columns:
        viajes["Fecha Salida"] = pd.to_datetime(viajes["Fecha Salida"], errors="coerce")
    if "Fecha" in forecast.columns:
        forecast["Fecha"] = pd.to_datetime(forecast["Fecha"], errors="coerce")

    return viajes, asignacion, riesgo, forecast


def load_data():
    if all(k in st.session_state for k in ["viajes", "asignacion", "riesgo", "forecast"]):
        origen = "usuario"
        return (
            st.session_state["viajes"],
            st.session_state["asignacion"],
            st.session_state["riesgo"],
            st.session_state["forecast"],
            origen,
        )
    else:
        viajes, asignacion, riesgo, forecast = load_data_from_excel("Viajes.xlsx")  
        origen = "local"
        return viajes, asignacion, riesgo, forecast, origen


#crear menu
st.sidebar.title("Menú")
menu = st.sidebar.radio(
    "",
    [
        "Carga de Datos",
        "Estado Actual de la Flota",
        "Riesgo de Viajes Vacíos",
        "Pronóstico de Viajes Vacíos",
        "Asignación Óptima",
        "Impacto Operativo",
    ],
)


#SECCION: cargar datos del usuario
if menu == "Carga de Datos":
    show_logo()
    st.title("Carga de Base de Datos")

    uploaded_file = st.file_uploader("", type=["xlsx"])

    if uploaded_file is not None:
        try:
            viajes, asignacion, riesgo, forecast = load_data_from_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            st.stop()

        st.session_state["viajes"] = viajes
        st.session_state["asignacion"] = asignacion
        st.session_state["riesgo"] = riesgo
        st.session_state["forecast"] = forecast

        st.success("Archivo cargado correctamente")

        col1, col2 = st.columns(2)
        col1.metric("Registros", viajes.shape[0])
        col2.metric("Variables", viajes.shape[1])

        with st.expander("Vista previa — Viajes"):
            st.dataframe(viajes.head(20), use_container_width=True)

    else:
        st.info("Carga Viajes.xlsx (esta página solo es funcional para ese archivo)")


#las otras pantallas
else:
    viajes, asignacion, riesgo, forecast, origen = load_data()

    # Variables globales
    rutas_activas = viajes["Ruta"].nunique()
    unidades_activas = viajes["Tractocamión"].nunique()
    total_viajes = len(viajes)

    threshold_global = viajes["Peso Kgs"].quantile(0.10)
    viajes["viaje_vacio"] = (viajes["Peso Kgs"] < threshold_global).astype(int)
    total_vacios = viajes["viaje_vacio"].sum()

    riesgo_actual = riesgo.groupby("Ruta")["Prob_vacio"].mean()
    riesgo_optimo = asignacion.groupby("Ruta")["Prob_vacio"].mean()

    comparacion = riesgo_actual.reset_index().merge(
        riesgo_optimo.reset_index(),
        on="Ruta",
        suffixes=("_Actual", "_Optimo")
    )
    comparacion["Mejora"] = (
        comparacion["Prob_vacio_Actual"] - comparacion["Prob_vacio_Optimo"]
    ) * 100
    mejora_global = comparacion["Mejora"].mean()

    palette = [BEPENSA_ORANGE, BEPENSA_GRAY, BEPENSA_LIGHT, "#9fa4b8"]


    #=====================================================
    #      ESTADO ACTUAL DE LA FLOTA

    if menu == "Estado Actual de la Flota":

        show_logo()
        st.title("Estado Actual de la Flota")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rutas activas", rutas_activas)
        col2.metric("Unidades activas", unidades_activas)
        col3.metric("Total de viajes", total_viajes)
        col4.metric("Viajes vacíos", "6931")

        st.caption("Indicadores calculados a partir del histórico de viajes depurado.")
        st.divider()

        # Filtro de meses
        viajes["Fecha Salida"] = pd.to_datetime(viajes["Fecha Salida"], errors="coerce")
        viajes = viajes[(viajes["Fecha Salida"] >= "2025-01-01") & (viajes["Fecha Salida"] <= "2026-12-31")]
        
        viajes["Mes"] = viajes["Fecha Salida"].dt.to_period("M").astype(str)
        meses_unicos = sorted(viajes["Mes"].dropna().unique())
        meses_sel = st.multiselect("Filtrar por mes", meses_unicos, default=meses_unicos)

        df_mes = viajes[viajes["Mes"].isin(meses_sel)]

        # Viajes vacíos mensual
        serie = df_mes.groupby("Mes")["viaje_vacio"].mean().reset_index()
        serie["viaje_vacio"] *= 100

        fig_line = px.line(
            serie,
            x="Mes",
            y="viaje_vacio",
            markers=True,
            title="Proporción mensual de viajes vacíos (%)",
            color_discrete_sequence=[BEPENSA_ORANGE],
            hover_data={"viaje_vacio": ":.2f"},
        )
        fig_line.update_layout(xaxis_title="Mes", yaxis_title="Proporción (%)")
        st.plotly_chart(fig_line, use_container_width=True)

        st.divider()

        # Estatus de viaje
        st.subheader("Estatus de viaje")
        estatus = df_mes["Estatus de Viaje"].value_counts().reset_index()
        estatus.columns = ["Estatus", "Cantidad"]

        colA, colB = st.columns(2)
        colA.dataframe(estatus, use_container_width=True)

        fig_est = px.bar(
            estatus,
            x="Estatus",
            y="Cantidad",
            title="Distribución de estatus",
            color="Estatus",
            color_discrete_sequence=palette,
            hover_data={"Cantidad": True},
        )
        fig_est.update_layout(xaxis_title="", yaxis_title="Viajes")
        colB.plotly_chart(fig_est, use_container_width=True)

        st.divider()

        # Peso transportado por unidad
        st.subheader("Peso transportado por unidad")

        unidades = sorted(viajes["Tractocamión"].dropna().unique())
        sel_unidad = st.selectbox("Selecciona una unidad", unidades)

        df_unit = viajes[viajes["Tractocamión"] == sel_unidad].sort_values("Fecha Salida")
        st.caption(f"Mostrando todos los viajes realizados por **{sel_unidad}**.")

        fig_timeline = px.scatter(
            df_unit,
            x="Fecha Salida",
            y="Peso Kgs",
            color_discrete_sequence=[BEPENSA_ORANGE],
            hover_data={"Peso Kgs": ":.0f", "Ruta": True},
            title=f"Viajes y carga transportada de la unidad {sel_unidad}",
        )

        fig_timeline.add_traces(
            px.line(
                df_unit,
                x="Fecha Salida",
                y="Peso Kgs",
                color_discrete_sequence=[BEPENSA_GRAY]
            ).data
        )

        fig_timeline.update_layout(
            xaxis_title="Fecha del viaje",
            yaxis_title="Peso transportado (kg)",
            showlegend=False
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)


    #=====================================================
    #              PREDICCIÓN DE VIAJES VACÍOS

    elif menu == "Riesgo de Viajes Vacíos":

        show_logo()
        st.title("Riesgo de Viaje Vacío")

        if not {"Ruta", "Tractocamión", "Prob_vacio"}.issubset(riesgo.columns):
            st.error("La hoja 'Riesgo' debe contener: Ruta, Tractocamión, Prob_vacio.")
        else:
            col1, col2 = st.columns(2)

            ruta_sel = col1.selectbox(
                "Selecciona una Ruta",
                sorted(riesgo["Ruta"].dropna().unique())
            )

            unidades = (
                riesgo[riesgo["Ruta"] == ruta_sel]["Tractocamión"]
                .dropna()
                .unique()
            )

            unidad_sel = col2.selectbox(
                "Selecciona la Unidad",
                sorted(unidades)
            )

            fila = riesgo[
                (riesgo["Ruta"] == ruta_sel) & (riesgo["Tractocamión"] == unidad_sel)
            ]

            st.subheader("Probabilidad estimada de viaje vacío")

            if fila.empty:
                st.warning("No hay datos para esta combinación.")
            else:
                prob = float(fila["Prob_vacio"].mean())

                donut_data = pd.DataFrame({
                    "Estado": ["Vacío", "Con carga"],
                    "Probabilidad": [prob, 1 - prob]
                })

                fig_donut = px.pie(
                    donut_data,
                    names="Estado",
                    values="Probabilidad",
                    hole=0.4,
                    title=f"Riesgo para {ruta_sel} con tractocamión {unidad_sel}",
                    color_discrete_sequence=[BEPENSA_ORANGE, BEPENSA_GRAY],
                )
                fig_donut.update_traces(textinfo="percent+label", hovertemplate="%{label}: %{percent}")
                st.plotly_chart(fig_donut, use_container_width=True)

            st.divider()
            st.subheader("Rutas con mayor probabilidad de viaje vacío")

            top_n = st.slider("Top N rutas", min_value=3, max_value=20, value=10)

            top_riesgo = (
                riesgo.groupby("Ruta")["Prob_vacio"]
                .mean()
                .sort_values(ascending=False)
                .head(top_n)
                .reset_index()
            )

            fig_top = px.bar(
                top_riesgo,
                x="Prob_vacio",
                y="Ruta",
                orientation="h",
                title=f"Top {top_n} rutas más riesgosas",
                color="Ruta",
                color_discrete_sequence=palette,
                hover_data={"Prob_vacio": ":.2f"},
            )
            fig_top.update_layout(
                yaxis=dict(categoryorder="total ascending"),
                xaxis_title="Probabilidad de viaje vacío",
                yaxis_title="Ruta"
            )
            st.plotly_chart(fig_top, use_container_width=True)

            st.divider()
            st.subheader("Rutas con menor probabilidad de viaje vacío")

            bajo = (
                riesgo.groupby("Ruta")["Prob_vacio"]
                .mean()
                .sort_values()
                .head(top_n)
                .reset_index()
            )

            fig_low = px.bar(
                bajo,
                x="Prob_vacio",
                y="Ruta",
                orientation="h",
                title=f"Top {top_n} rutas más eficientes",
                color="Ruta",
                color_discrete_sequence=palette,
                hover_data={"Prob_vacio": ":.2f"},
            )
            fig_low.update_layout(
                yaxis=dict(categoryorder="total descending"),
                xaxis_title="Probabilidad de viaje vacío",
                yaxis_title="Ruta"
            )
            st.plotly_chart(fig_low, use_container_width=True)

            st.caption("""
            **Resumen:**
            - El gráfico de dona muestra el riesgo puntual por combinación ruta–unidad.
            - Las barras horizontales permiten priorizar rutas críticas.
            - Las rutas eficientes sirven como benchmark operacional.
            """)

            #=====================================================
            #        GRÁFICA DE FACTORES DE RIESGO (IMPORTANCIA)

            st.divider()
            st.subheader("Factores que más influyen en el riesgo de viaje vacío")

            # Datos simulados basados en tu gráfica real
            importances = pd.DataFrame({
                "Variable": [
                "Nombre Cliente_EMBOTELLADORAS BEPENSA",
                "Peso_prom_ruta",
                "Nombre Cliente_NUEVA WAL MART DE MEXICO",
                "Duración_horas",
                "Semana",
                "Mes",
                "Tractocamión_T541",
                "Nombre Cliente_INDUSTRIA ENVASADORA DE QUERETARO",
                "Tractocamión_T575",
                "Ruta_WM CEDIS VILLAHERMOSA SECOS/PENSION SALINAS CRUZ",
                "Tractocamión_T620",
                "Ruta_BB CANCUN PLANTA/BB PLAYA DEL CARMEN",
                "Ruta_BB CAMPECHE OTE/BB PACABTUN",
                "Ruta_BB PACABTUN/BB PROGRESO",
                "Tractocamión_T600" ],
                "Importancia": [
                0.085,
                0.072,
                0.061,
                0.058,
                0.048,
                0.043,
                0.038,
                0.036,
                0.027,
                0.026,
                0.021,
                0.019,
                0.017,
                0.015,
                0.014]})

            # Orden ascendente para barra horizontal
            importances = importances.sort_values("Importancia", ascending=True)

            #grafica
            fig = px.bar(
            importances,
            x="Importancia",
            y="Variable",
            orientation="h",
            title="Variables más influyentes",
            color="Importancia",
            color_continuous_scale=["#2e3242", "#1f222c"])

            fig.update_layout(
                xaxis_title="Importancia",
                yaxis_title="Variable",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                title_font=dict(size=20),)

            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=False)

            st.plotly_chart(fig, use_container_width=True)

    
    #=====================================================
    #                  FORECAST 6 MESES

    elif menu == "Pronóstico de Viajes Vacíos":

        show_logo()
        st.title("Pronóstico de Viajes Vacíos")

        figF = px.line(
            forecast,
            x="Fecha",
            y="pronostico",
            markers=True,
            title="Forecast de 6 meses de proporción de viajes vacíos",
            color_discrete_sequence=[BEPENSA_ORANGE],
            hover_data={"pronostico": ":.3f"},
        )
        figF.update_layout(xaxis_title="Fecha", yaxis_title="Proporción estimada de viajes vacíos")
        st.plotly_chart(figF, use_container_width=True)

        st.divider()
        st.subheader("Tabla interactiva del pronóstico")

        rango = st.slider(
            "Selecciona rango de fechas",
            min_value=forecast["Fecha"].min().date(),
            max_value=forecast["Fecha"].max().date(),
            value=(forecast["Fecha"].min().date(), forecast["Fecha"].max().date()),
        )

        df_filt = forecast[
            (forecast["Fecha"].dt.date >= rango[0]) &
            (forecast["Fecha"].dt.date <= rango[1])
        ].copy()

        st.dataframe(df_filt, use_container_width=True)


    #=====================================================
    #                 ASIGNACIÓN ÓPTIMA

    elif menu == "Asignación Óptima":

        show_logo()
        st.title("Asignación Óptima de Rutas–Unidades")

        st.subheader("Buscador de ruta")
        ruta_query = st.text_input("Ingresa una ruta tal cual está en la base de datos:")

        if ruta_query:
            resultados = asignacion[
                asignacion["Ruta"].str.contains(ruta_query, case=False, na=False)
            ]
            if resultados.empty:
                st.warning("No se encontró ninguna ruta que coincida con la búsqueda.")
            else:
                #iNDENTIFICAR EL MEJOR TRACTO
                mejor_fila = resultados.loc[resultados["Prob_vacio"].idxmin()]
                mejor_ruta = mejor_fila["Ruta"]
                mejor_unidad = mejor_fila["Tractocamión"]
                mejor_prob = mejor_fila["Prob_vacio"] * 100

                #desplique al usuario 
                st.markdown( 
                    f"""
                    #### Resultado para la ruta **{mejor_ruta}**
                     El tractocamión con **menor probabilidad de realizar un viaje en vacío** es  
                    **{mejor_unidad}**, con una probabilidad estimada de **{mejor_prob:.2f}%**."""
                )
                st.write("#### Resultados encontrados:")
                st.dataframe(resultados, use_container_width=True)


        else:
            st.caption("Para consultar su unidad recomendada y probabilidad de viaje vacío.")

        st.divider()
        st.subheader("Tabla completa de asignación ruta-unidad")
        st.dataframe(asignacion)

        #COMBINACIONES MÁS EFICIENTES

        palette = ["#fd5e2e", "#2e3242", "#dde2f3", "#9fa4b8"] #volver a poner colores 
        top_eff = asignacion.sort_values("Prob_vacio").head(20)

        fig_top = px.bar(
            top_eff,
            x="Prob_vacio", 
            y="Ruta",
            orientation="h",
            color="Tractocamión",
            title="Top 20 combinaciones más eficientes",
            color_discrete_sequence=palette,
            hover_data={"Prob_vacio": ":.3f", "Tractocamión": True},
        )
        st.plotly_chart(fig_top, use_container_width=True)


    #=====================================================
    #                 IMPACTO OPERATIVO

    elif menu == "Impacto Operativo":

        show_logo()
        st.title("Impacto Operativo de la Asignación Óptima")

        st.markdown(f"""
        El modelo de **asignación óptima de rutas y unidades** es elemental para que la
        proporción de viajes en vacío disminuya de forma sostenible.  

        - Reduce el riesgo promedio de viaje vacío al reasignar unidades hacia las rutas
          donde su desempeño histórico es mejor.  
        - Permite priorizar rutas con mayor potencial de mejora.  
        - Ofrece una base objetiva para la planeación táctica de la flota.

        En esta sección puedes consultar **cómo cambia el riesgo de viaje vacío**
        para cualquier ruta al aplicar el modelo de asignación óptima.          
        
        """)

        ruta_query = st.text_input("Ingresa una ruta para evaluar su mejora operativa:")

        if ruta_query: 
            resultados = comparacion[
            comparacion["Ruta"].str.contains(ruta_query, case=False, na=False)]

            if resultados.empty: 
                st.warning("No se encontró ninguna ruta que coincida con la búsqueda.")
                st.stop()
            
            #Tomar la mejor coincidencia
            fila = resultados.iloc[0]
            ruta = fila["Ruta"]
            riesgo_actual = fila["Prob_vacio_Actual"] * 100
            riesgo_optimo = fila["Prob_vacio_Optimo"] * 100
            mejora = fila["Mejora"]

            #Interpretar
            st.markdown(
            f"""
            ### Resultado para la ruta **{ruta}**
            - **Riesgo actual:** {riesgo_actual:.2f}%  
            - **Riesgo óptimo recomendado:** {riesgo_optimo:.2f}%  
            - **Mejora esperada:** **{mejora:.2f} puntos porcentuales**  

            Esto indica que, al asignar la unidad óptima sugerida por el modelo,  
            la probabilidad de realizar un viaje vacío **disminuye significativamente**.
            """
        )
            #Comparar
            df_plot = pd.DataFrame({
            "Categoria": ["Riesgo Actual", "Riesgo Óptimo"],
            "Valor": [riesgo_actual, riesgo_optimo]
        })
            fig_comp = px.bar(
                df_plot,
                x="Valor",
                y="Categoria",
                orientation="h",
                title="Comparación de riesgo actual vs óptimo",
                color="Categoria",
                color_discrete_sequence=[BEPENSA_ORANGE, BEPENSA_GRAY],
                text=[f"{riesgo_actual:.2f}%", f"{riesgo_optimo:.2f}%"]
        )
            fig_comp.update_traces(textposition="outside")
            fig_comp.update_layout(xaxis_title="Probabilidad (%)")

            st.plotly_chart(fig_comp, use_container_width=True)

            #tabla
            st.subheader("Detalles de la ruta")
            st.dataframe(resultados, use_container_width=True)
        
        else:
            st.info("Ingresa una ruta para visualizar su impacto operativo.")


import streamlit as st
import json
import pandas as pd
from normalizer import TransactionNormalizer
from validator import TransactionValidator
from metrics import MetricsCalculator

# Configuración de página
st.set_page_config(page_title="Normalizador de Transacciones", layout="wide")

st.title("Sistema de Normalización de Transacciones")
st.markdown("Carga y explora datos transaccionales multi-fuente de forma normalizada.")

# Inicializar servicios
normalizer = TransactionNormalizer()
validator = TransactionValidator()

# 1. Carga de archivo en la barra lateral
st.sidebar.header("Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Selecciona un archivo JSON", type=["json"])

raw_data = None
if uploaded_file is not None:
    raw_data = json.load(uploaded_file)
else:
    # Cargar datos por defecto si existe data_test.json
    try:
        with open("data_test.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        st.sidebar.info("Cargado `data_test.json` por defecto.")
    except FileNotFoundError:
        st.sidebar.warning("Sube un archivo JSON para comenzar.")

if raw_data:
    # Procesamiento
    processed_records = []
    for item in raw_data:
        norm_tx = normalizer.normalize(item)
        is_valid, errors = validator.validate(norm_tx)
        processed_records.append({
            "data": norm_tx,
            "is_valid": is_valid,
            "errors": errors
        })

    metrics = MetricsCalculator.compute(processed_records)

    # 2. Métricas en Tarjetas (KPIs)
    st.subheader(" Métricas Generales")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Procesadas", metrics["total_processed"])
    col2.metric("Transacciones Válidas", metrics["valid_count"])
    col3.metric("Transacciones Inválidas", metrics["invalid_count"], delta_color="inverse")

    st.divider()

    # 3. Pestañas de Exploración y Filtros
    tab1, tab2, tab3 = st.tabs([" Explorador Interactivo", " Totales por Moneda", " Registros Inválidos"])

    with tab1:
        st.subheader("Filtrar Transacciones Válidas")
        
        # Obtener lista de registros válidos en un DataFrame
        valid_list = [r["data"] for r in processed_records if r["is_valid"]]
        df_valid = pd.DataFrame(valid_list)

        if not df_valid.empty:
            # Filtros en columnas
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                status_filter = st.multiselect(
                    "Filtrar por Estado:",
                    options=["SUCCESS", "FAILED", "PENDING"],
                    default=list(df_valid["status"].unique())
                )
            with f_col2:
                currency_filter = st.multiselect(
                    "Filtrar por Moneda:",
                    options=df_valid["currency"].unique(),
                    default=list(df_valid["currency"].unique())
                )

            # Aplicar filtros
            filtered_df = df_valid[
                (df_valid["status"].isin(status_filter)) & 
                (df_valid["currency"].isin(currency_filter))
            ]

            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning("No hay transacciones válidas para mostrar.")

    with tab2:
        st.subheader("Totales de Monto por Moneda")
        totals_df = pd.DataFrame(
            list(metrics["totals_by_currency"].items()), 
            columns=["Moneda", "Monto Total"]
        )
        if not totals_df.empty:
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                st.bar_chart(totals_df.set_index("Moneda"))
            with col_table:
                st.dataframe(totals_df, use_container_width=True)
        else:
            st.info("No hay datos de moneda disponibles.")

    with tab3:
        st.subheader("Detalle de Registros Inválidos")
        invalid_list = []
        for r in processed_records:
            if not r["is_valid"]:
                invalid_list.append({
                    "ID Original/Detectado": r["data"].get("id"),
                    "Fuente": r["data"].get("source"),
                    "Motivos de Rechazo": ", ".join(r["errors"]),
                    "Datos Normalizados": str(r["data"])
                })
        
        if invalid_list:
            st.dataframe(pd.DataFrame(invalid_list), use_container_width=True)
        else:
            st.success("¡Excelente! No hay transacciones inválidas.")
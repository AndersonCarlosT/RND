import streamlit as st
import pandas as pd

st.set_page_config(page_title="🧪 Depuración de Archivos", layout="wide")
st.title("🔍 Verificación de Archivos Cargados")

archivo_ref = st.file_uploader("📂 Sube el archivo principal (con PODs)", type=["xlsx"])
archivos_generacion = st.file_uploader("📂 Sube los archivos .csv de generación", type=["csv"], accept_multiple_files=True)

if archivo_ref:
    st.subheader("📄 Primer archivo cargado (Excel):")
    df_ref = pd.read_excel(archivo_ref, header=0)  # Usa encabezado en la primera fila
    st.write(df_ref.head())  # Muestra las primeras filas

if archivos_generacion:
    st.subheader("📄 Primer archivo .csv del segundo selectbox:")
    archivo_csv = archivos_generacion[0]
    df_raw = pd.read_csv(archivo_csv, header=None)
    
    st.write("Contenido crudo (una sola columna):")
    st.write(df_raw.head())  # Ver original
    
    # Intentar separar por comas
    df_split = df_raw[0].str.split(",", expand=True)
    st.write("Después de separar por comas:")
    st.write(df_split.head())

    st.info(f"Este archivo tiene {df_split.shape[1]} columnas después de separar por comas.")

import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="📊 Generación", layout="wide")
st.title("📁 Comparador de PODs y Generación")

# Subida del archivo principal
archivo_ref = st.file_uploader("📂 Sube el archivo principal con códigos de suministro, cliente y POD", type=["xlsx"])

# Subida de archivos de generación
archivos_generacion = st.file_uploader("📂 Sube los archivos de generación (.csv)", type=["csv"], accept_multiple_files=True)

if archivo_ref and archivos_generacion:
    df_ref = pd.read_excel(archivo_ref, header=None)
    
    cod_suministros = df_ref.iloc[:, 0]
    clientes = df_ref.iloc[:, 1]
    pods = df_ref.iloc[:, 5]

    # Limpiar datos
    df_meta = pd.DataFrame({
        "Suministro": cod_suministros,
        "Cliente": clientes,
        "POD": pods
    }).dropna()

    pods_unicos = df_meta["POD"].tolist()

    # Diccionario: POD -> (Suministro, Cliente)
    pod_to_meta = df_meta.set_index("POD")[["Suministro", "Cliente"]].to_dict(orient="index")

    fechas = []
    horas = []
    pod_data = {}

    for archivo in archivos_generacion:
        df_raw = pd.read_csv(archivo, header=None)
        df_split = df_raw[0].str.split(",", expand=True)

        if df_split.shape[1] < 4:
            st.error(f"⚠️ El archivo {archivo.name} no tiene suficientes columnas.")
            st.stop()

        pod_actual = df_split.iloc[1, 0]  # Asumimos que todas las filas tienen el mismo POD
        fechas.append(df_split.iloc[1:, 1].tolist())
        horas.append(df_split.iloc[1:, 2].tolist())
        valores_kwh = df_split.iloc[1:, 3].astype(float).tolist()  # Columna KWH_DEL_INT

        pod_data[pod_actual] = valores_kwh

    # Validar si todas las fechas y horas son iguales
    fechas_iguales = all(f == fechas[0] for f in fechas)
    horas_iguales = all(h == horas[0] for h in horas)

    if fechas_iguales and horas_iguales:
        base_df = pd.DataFrame({
            "Fecha": fechas[0],
            "Hora": horas[0]
        })

        # Encabezados jerárquicos
        row1 = ["", ""]  # Suministro
        row2 = ["", ""]  # Cliente
        row3 = ["Fecha", "Hora"]  # PODs

        # Agregar cada columna de POD coincidente
        for pod in pods_unicos:
            if pod in pod_data:
                meta = pod_to_meta.get(pod, {"Suministro": "", "Cliente": ""})
                row1.append(meta["Suministro"])
                row2.append(meta["Cliente"])
                row3.append(pod)
                base_df[pod] = pod_data[pod]
            else:
                row1.append("")
                row2.append("")
                row3.append(pod)
                base_df[pod] = [""] * len(base_df)

        # Crear Excel con encabezado desde fila 3 (índice 2)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            base_df.to_excel(writer, index=False, startrow=3, header=False, sheet_name="Generacion")
            workbook = writer.book
            worksheet = writer.sheets["Generacion"]

            # Escribir filas de encabezado jerárquico manualmente
            for col_num, (s, c, p) in enumerate(zip(row1, row2, row3)):
                worksheet.write(0, col_num, s)
                worksheet.write(1, col_num, c)
                worksheet.write(2, col_num, p)

        output.seek(0)

        st.success("✅ Archivo generado exitosamente.")
        st.download_button(
            label="📥 Descargar archivo 'Generacion.xlsx'",
            data=output,
            file_name="Generacion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.error("❌ Las fechas y/u horas no son iguales en todos los archivos.")

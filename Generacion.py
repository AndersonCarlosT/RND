import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="📊 Generación", layout="wide")
st.title("📁 Comparador de PODs y Generación")

# Subida del archivo principal
archivo_ref = st.file_uploader("📂 Sube el archivo principal con códigos de suministro, cliente y POD", type=["xlsx"])

# Subida de archivos de generación (csv)
archivos_generacion = st.file_uploader("📂 Sube los archivos de generación (.csv)", type=["csv"], accept_multiple_files=True)

if archivo_ref and archivos_generacion:
    # Leer el archivo principal (con encabezados en la fila 1)
    df_ref = pd.read_excel(archivo_ref, header=0)
    
    cod_suministros = df_ref.iloc[:, 0]
    clientes = df_ref.iloc[:, 1]
    pods = df_ref.iloc[:, 5]

    df_meta = pd.DataFrame({
        "Suministro": cod_suministros,
        "Cliente": clientes,
        "POD": pods
    }).dropna()

    pods_unicos = df_meta["POD"].tolist()
    pod_to_meta = df_meta.set_index("POD")[["Suministro", "Cliente"]].to_dict(orient="index")

    fechas = []
    horas = []
    pod_data = {}

    for archivo in archivos_generacion:
        df_raw = pd.read_csv(archivo, header=None)

        if df_raw.shape[1] < 4:
            st.error(f"⚠️ El archivo {archivo.name} no tiene suficientes columnas.")
            st.stop()

        pod_actual = df_raw.iloc[1, 0]
        fechas.append(df_raw.iloc[1:, 1].tolist())
        horas.append(df_raw.iloc[1:, 2].tolist())
        valores_kwh = df_raw.iloc[1:, 3].astype(float).tolist()

        pod_data[pod_actual] = valores_kwh

    # Verificar si las fechas y horas son iguales en todos los archivos
    fechas_iguales = all(f == fechas[0] for f in fechas)
    horas_iguales = all(h == horas[0] for h in horas)

    if fechas_iguales and horas_iguales:
        # Crear base del DataFrame final
        base_df = pd.DataFrame({
            "Fecha": fechas[0],
            "Hora": horas[0]
        })

        row1 = ["", ""]  # Fila 1: Códigos de suministro
        row2 = ["", ""]  # Fila 2: Clientes
        row3 = ["Fecha", "Hora"]  # Fila 3: PODs

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

        # Generar Excel con encabezado en filas 1-3 (A1:B3)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            base_df.to_excel(writer, index=False, startrow=3, header=False, sheet_name="Generacion")
            worksheet = writer.sheets["Generacion"]

            # Escribir encabezados jerárquicos manualmente
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

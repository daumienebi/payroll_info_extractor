import streamlit as st
import PyPDF2
import json
import pandas as pd
from openai import OpenAI
import io

# =====================================================================
# CONFIGURACIÓN DE LA PÁGINA Y API
# =====================================================================
st.set_page_config(page_title="Extractor IA de Nóminas", layout="centered")

client = OpenAI(base_url="http://localhost:1234/v1", api_key="local-api-key")

# =====================================================================
# FUNCIONES (Misma lógica de antes)
# =====================================================================
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        # Streamlit pasa el archivo como un objeto en memoria, PyPDF2 lo lee directo
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return None

def analyze_document_with_llm(text):
    prompt = f"""
    You are an expert data extraction assistant. 
    Read the following payroll (nómina) document and extract the key information.
    
    You MUST return ONLY a valid JSON object with the following keys. Do not add markdown formatting or explanations.
    - "empresa": Name of the company.
    - "cif": CIF of the company.
    - "empleado": Name of the employee.
    - "puesto": Job position (Puesto).
    - "contrato": Type of contract (Contrato).
    - "periodo": Period of the payroll (e.g., Junio 2026).
    - "salario_base": Base salary amount.
    - "salario_bruto": Total devengado / Gross salary.
    - "total_deducciones": Total deducciones / Total deductions.
    - "salario_neto": Líquido a percibir / Net salary.

    Document text:
    {text}
    """
    try:
        response = client.chat.completions.create(
            model="local-model", 
            messages=[
                {"role": "system", "content": "You output ONLY valid JSON objects. No markdown, no text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        raw_response = response.choices[0].message.content.strip()
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:-3].strip()
        elif raw_response.startswith("```"):
            raw_response = raw_response[3:-3].strip()
        return json.loads(raw_response)
    except Exception as e:
        return None

# =====================================================================
# INTERFAZ DE USUARIO (WEB)
# =====================================================================
st.title("📄 Extractor de Nóminas Inteligente")
st.write("Sube hasta 5 nóminas en PDF para extraer sus datos automáticamente usando IA Local (Llama 3.1).")

# 1. Zona de subida de archivos
archivos_subidos = st.file_uploader("Arrastra tus PDFs aquí (Máximo 5)", type="pdf", accept_multiple_files=True)

if archivos_subidos:
    # Límite de 5 archivos
    if len(archivos_subidos) > 5:
        st.warning("⚠️ Por favor, selecciona un máximo de 5 archivos.")
    else:
        # Botón para iniciar el proceso
        if st.button("🚀 Procesar Nóminas"):
            datos_extraidos = []
            barra_progreso = st.progress(0)
            
            # 2. Bucle de procesamiento
            with st.spinner('Conectando con el LLM Local y analizando documentos...'):
                for i, pdf_file in enumerate(archivos_subidos):
                    text = extract_text_from_pdf(pdf_file)
                    if text:
                        resultado_json = analyze_document_with_llm(text)
                        if resultado_json:
                            resultado_json["archivo_origen"] = pdf_file.name
                            datos_extraidos.append(resultado_json)
                    # Actualizar barra de progreso
                    barra_progreso.progress((i + 1) / len(archivos_subidos))
            
            # 3. Mostrar resultados y botón de descarga
            if datos_extraidos:
                st.success("¡Análisis completado con éxito!")
                df = pd.DataFrame(datos_extraidos)
                
                # Reordenar columnas
                column_order = [
                    "archivo_origen", "empresa", "cif", "periodo", "empleado", 
                    "puesto", "contrato", "salario_base", "salario_bruto", 
                    "total_deducciones", "salario_neto"
                ]
                df = df.reindex(columns=[c for c in column_order if c in df.columns])
                
                # Mostrar tabla en la web
                st.dataframe(df)
                
                # Preparar el archivo Excel en memoria
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                # Botón de descarga
                st.download_button(
                    label="📥 Descargar datos en Excel",
                    data=buffer.getvalue(),
                    file_name="resumen_nominas_ia.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("No se pudo extraer información de los documentos.")
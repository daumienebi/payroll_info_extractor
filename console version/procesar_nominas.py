import os
import glob
import PyPDF2
import json
import pandas as pd
from openai import OpenAI

# =====================================================================
# 1. CONFIGURACIÓN DEL CLIENTE API
# =====================================================================
client = OpenAI(
    base_url="http://localhost:1234/v1", 
    api_key="local-api-key"
)

# =====================================================================
# 2. FUNCIÓN PARA LEER PDF
# =====================================================================
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error leyendo {pdf_path}: {e}")
        return None

# =====================================================================
# 3. EXTRACCIÓN CON EL LLM (Llama 3.1 8B)
# =====================================================================
def analyze_document_with_llm(text):
    # Prompt ampliado para extraer muchos más datos de la nómina
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
            temperature=0.0 # Temperatura 0 para que no invente nada
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        # Limpieza por si el modelo añade etiquetas markdown
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:-3].strip()
        elif raw_response.startswith("```"):
            raw_response = raw_response[3:-3].strip()
            
        return json.loads(raw_response)
    
    except Exception as e:
        print(f"Error procesando con LLM: {e}")
        return None

# =====================================================================
# 4. EJECUCIÓN PRINCIPAL (LOTE DE ARCHIVOS A EXCEL)
# =====================================================================
if __name__ == "__main__":
    pdf_files = glob.glob("*.pdf")
    
    if not pdf_files:
        print("No se han encontrado archivos PDF en la carpeta.")
        exit()
        
    print(f"Se han encontrado {len(pdf_files)} archivos PDF. Iniciando procesamiento...\n")
    
    datos_extraidos = []

    for pdf_file in pdf_files:
        print(f"Procesando: {pdf_file}...")
        text = extract_text_from_pdf(pdf_file)
        
        if text:
            resultado_json = analyze_document_with_llm(text)
            if resultado_json:
                resultado_json["archivo_origen"] = pdf_file
                datos_extraidos.append(resultado_json)
                print(f"  -> ¡Éxito! Empleado: {resultado_json.get('empleado')} | Neto: {resultado_json.get('salario_neto')}")
            else:
                print("  -> Fallo en la extracción JSON.")
    
    # Guardar SOLAMENTE en Excel
    if datos_extraidos:
        df = pd.DataFrame(datos_extraidos)
        
        # Reordenamos un poco las columnas para que el Excel quede más bonito y lógico
        column_order = [
            "archivo_origen", "empresa", "cif", "periodo", "empleado", 
            "puesto", "contrato", "salario_base", "salario_bruto", 
            "total_deducciones", "salario_neto"
        ]
        # Asegurarnos de que todas las columnas existen por si el LLM omitió alguna
        df = df.reindex(columns=[c for c in column_order if c in df.columns])
        
        excel_filename = "resumen_nominas.xlsx"
        df.to_excel(excel_filename, index=False)
        print(f"\n=======================================================")
        print(f"¡Proceso completado! Datos guardados en: {excel_filename}")
        print(f"=======================================================")
    else:
        print("\nNo se pudo extraer información de ningún archivo.")
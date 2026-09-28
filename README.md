# Extracting Information from Payrolls using Local LLMs

This project demonstrates how to use a local Large Language Model (LLM) to automatically extract structured data from PDF payrolls ("nóminas") and export the results to an Excel spreadsheet. The project is divided into two different versions: a Console Application and a Web Interface. 

Both project folders already contain the sample PDF payrolls needed to run the tests.

## Prerequisites

Before running any of the versions, you must install and configure **two main components**:

### 1. Local LLM Server (LM Studio)
You need a local server running an OpenAI-compatible API to process the documents locally without internet constraints.
1. Download and install [LM Studio](https://lmstudio.ai/).
2. Download an Instruct model (e.g., `Meta-Llama-3.1-8B-Instruct-GGUF`).
3. **Important for Performance:** Go to the Hardware Settings on the right panel and maximize the **GPU Offload** (e.g., 32 layers) to ensure the model runs entirely on the GPU VRAM.
4. Go to the **Local Server** tab, select the model, and click **Start Server**. Ensure it is running on `http://localhost:1234/v1`.

### 2. Python Dependencies
You must install the required Python libraries to process the PDFs, connect to the local API, manage data frames, and render the web interface. Open your terminal and run:
```bash
pip install PyPDF2 openai pandas openpyxl streamlit
```

---

## Version 1: Console Application

This version automatically scans its directory for all available PDF files, processes them in bulk, and generates a formatted Excel file.

**Steps to test:**
1. Open a terminal and navigate to the folder containing the console version.
2. Ensure the sample PDFs are located in the same directory as the script.
3. Run the Python script:
   ```bash
   python payroll_info_extractor.py
   ```
4. The terminal will display the extraction progress and the parsed JSON data in real-time.
5. Once finished, a file named `resumen_nominas.xlsx` will be generated in the same folder containing all the structured data.

---

## Version 2: Web Interface (Streamlit)

This version provides a user-friendly graphical web interface that allows users to manually upload up to 5 payroll PDFs, view the extracted data in a table, and download the resulting spreadsheet.

**Steps to test:**
1. Open a terminal and navigate to the folder containing the web version.
2. Install Streamlit (if you haven't already) by running:
   ```bash
   pip install streamlit```
3. Start the Streamlit application by running:
   ```bash
   streamlit run app.py```
4. Your default web browser will automatically open the app at `http://localhost:8501`.
5. Drag and drop the sample PDFs from the folder into the upload area of the web interface.
6. Click **"Procesar Nóminas"** to start the extraction. A progress bar will indicate the status.
7. Once the process is complete, a data table will appear on the screen, along with a button to download the results directly as `resumen_nominas_ia.xlsx`.

---

## Evaluation Notes
* **Prompt Engineering:** The internal prompts are explicitly written in English to maximize the LLM's instruction-following capabilities, strictly enforcing a JSON output format with a `temperature=0.0` to avoid hallucinations.
* **OpenAI Drop-in Replacement:** The code uses the official `openai` Python package pointing to a local `base_url`. This allows the application to be completely agnostic; it can switch from a local 8B model to a cloud-based commercial model without rewriting the logic.
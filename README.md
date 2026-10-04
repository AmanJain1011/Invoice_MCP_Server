# Invoice Intelligence MCP Server

An AI-powered invoice extraction system that converts PDF, TXT, CSV, and Excel invoices into structured JSON using a Groq-hosted LLM. The extraction pipeline validates the output with Pydantic and performs a basic invoice total consistency check.

The project also exposes the invoice extraction functionality as **MCP (Model Context Protocol) tools**, allowing compatible AI clients such as Claude Desktop to discover and invoke the tools.

## ✨ Features

- 📄 Supports **PDF, TXT, CSV, and XLSX** invoice files
- 🤖 Uses a **Groq-hosted LLM** for invoice understanding and structured extraction
- 🌐 Supports **English, Hindi, and Hinglish** invoice text
- 🧩 Converts different file formats into plain text before LLM processing
- 📦 Returns structured invoice data as JSON
- ✅ Uses **Pydantic** for schema validation
- 🧮 Checks whether line items + tax are consistent with the invoice total
- 🛠️ Exposes `extract_invoice` and `extract_folder` as **MCP tools**
- 🧪 Includes offline testing with a mock LLM and live testing with Groq
- 🔐 API credentials are kept outside the repository using `.env`

---

## 🏗️ Architecture

```text
                Invoice File
          PDF / TXT / CSV / XLSX
                     │
                     ▼
               readers.py
                     │
             Convert to text
                     │
                     ▼
                Groq LLM
                     │
          Structured JSON output
                     │
                     ▼
                schema.py
             Pydantic validation
                     │
                     ▼
             Total consistency
                  check
                     │
                     ▼
              Invoice Result
                     │
             ┌───────┴────────┐
             │                │
             ▼                ▼
        Normal Python      MCP Server
          usage           mcp_server.py
                              │
                              ▼
                       Claude / MCP Client
```

### What each component does

| Component | Responsibility |
|---|---|
| `readers.py` | Reads PDF/TXT/CSV/XLSX files and converts their contents into text |
| Groq LLM | Understands invoice text and extracts the required fields |
| `schema.py` | Defines and validates the expected invoice structure using Pydantic |
| `extractor.py` | Connects document reading, LLM extraction, validation, and total checking |
| `mcp_server.py` | Exposes invoice functionality as MCP tools |
| `test_offline.py` | Tests the pipeline without calling the Groq API |
| `test_live.py` | Tests extraction using the configured Groq API |

---

## 🔄 Extraction Flow

```text
1. User provides an invoice file
             ↓
2. Appropriate reader is selected
             ↓
3. File content is converted to plain text
             ↓
4. Text is sent to the Groq LLM
             ↓
5. LLM returns structured JSON
             ↓
6. Pydantic validates the JSON structure
             ↓
7. Invoice totals are checked
             ↓
8. Final structured invoice result is returned
```

The LLM is instructed to return only the required JSON fields, avoid inventing missing values, preserve names/items in their original language, and use `null` when information is unavailable.

---

## 🧠 Why Groq?

Groq is used as the LLM inference provider in this project.

The application sends the extracted invoice text to the model along with instructions describing the required JSON structure.

Conceptually:

```text
Invoice Text
     ↓
Groq-hosted LLM
     ↓
Understand invoice
     ↓
Extract fields
     ↓
Structured JSON
```

Groq is therefore responsible for the **language understanding and information extraction** part of the pipeline.

---

## 🔌 Why MCP?

MCP is **not required for invoice extraction itself**.

The extraction pipeline can work as a normal Python application:

```text
Invoice → Python → Groq → JSON
```

MCP is added to expose the existing invoice-processing functionality as standardized tools that an AI client can discover and invoke.

This project exposes:

### `extract_invoice`

Processes a single invoice file.

### `extract_folder`

Processes multiple supported invoice files from a folder.

Conceptually:

```text
Claude Desktop
      │
      ▼
 MCP Protocol
      │
      ▼
MCP Server
      │
      ▼
Python invoice functions
      │
      ▼
Groq
      │
      ▼
Structured result
```

MCP therefore acts as the **AI-to-tool integration layer**, while Groq performs the LLM-based extraction.

---

## 📁 Project Structure

```text
invoice-mcp-server/
│
├── schema.py
├── readers.py
├── extractor.py
├── mcp_server.py
│
├── test_offline.py
├── test_live.py
├── requirements.txt
├── .env.example
├── .gitignore
│
└── samples/
    ├── invoice_en.pdf
    ├── invoice_en.txt
    ├── invoice_en.xlsx
    ├── invoice_hi.txt
    └── invoice_hinglish.csv
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/AmanJain1011/Invoice_MCP_Server.git
cd Invoice_MCP_Server
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Never commit the `.env` file to GitHub.

---

## 🧪 Testing

### Offline test

The offline test uses a fake/mock LLM response, so an API key is not required.

```powershell
python .\test_offline.py
```

### Live test

Provide the path of an invoice file:

```powershell
python .\test_live.py ".\samples\invoice_en.pdf"
```

Example result:

```json
{
  "invoice_number": "INV-2026-0142",
  "vendor_name": "Sharma Electronics, Jaipur",
  "customer_name": "Aman Traders",
  "subtotal": 18000,
  "tax_amount": 3240,
  "total_amount": 21240,
  "checks": {
    "total_matches": true
  }
}
```

The exact output depends on the input invoice.

---

## 🛠️ MCP Server

The MCP server is defined in:

```text
mcp_server.py
```

It exposes two tools:

```text
extract_invoice(file_path)
extract_folder(folder_path)
```

The server uses **stdio transport**, allowing local MCP clients such as Claude Desktop or MCP Inspector to communicate with it.

To test the server with MCP Inspector, use the MCP Inspector tooling with:

```powershell
npx @modelcontextprotocol/inspector .\venv\Scripts\python.exe .\mcp_server.py
```

---

## 🤝 Claude Desktop Integration

The MCP server can be configured as a local MCP server in Claude Desktop.

Example configuration:

```json
{
  "mcpServers": {
    "invoice-extractor": {
      "command": "E:\\invoice_mcp\\invoice_mcp\\venv\\Scripts\\python.exe",
      "args": [
        "E:\\invoice_mcp\\invoice_mcp\\mcp_server.py"
      ]
    }
  }
}
```

Use your own local paths when configuring the server.

> **Note:** A local MCP server runs on the machine where it is configured. A cloud deployment would be required for remote multi-user access.

---

## 🌍 Multilingual Support

The extraction prompt is designed to handle invoice text in:

- English
- Hindi
- Hinglish

The application uses UTF-8 text handling and normalizes Devanagari digits where required.

The LLM is instructed to preserve vendor names and item descriptions in their original language while keeping the output field names standardized.

---

## ✅ Validation & Reliability

The project uses multiple layers of validation:

### 1. Structured output

The LLM is requested to return JSON rather than free-form text.

### 2. Pydantic validation

The returned JSON is validated against the invoice schema.

### 3. Total consistency check

The application compares the invoice total with:

```text
subtotal + tax
```

and also considers the sum of line-item amounts where applicable.

These checks help detect inconsistent or incorrectly extracted invoice values.

---

## ⚠️ Current Limitations

- Scanned/image-only PDFs are not processed with OCR.
- Some Hindi PDFs may have problematic font encoding.
- The current MCP setup is intended for local use.
- The project does not currently provide authentication or multi-user remote deployment.
- LLM extraction can still require validation for unusual invoice layouts.

---

## 🚀 Future Improvements

- OCR support for scanned invoices
- Duplicate invoice detection
- Invoice database/search
- Excel/CSV export
- Automated invoice reports
- Better document/layout handling
- Secure remote MCP deployment
- Authentication and access control
- Integration with accounting or ERP systems

---

## 💡 Key Takeaway

This project combines three different responsibilities:

```text
Groq
→ Provides LLM-based invoice understanding

Python
→ Handles file reading, extraction pipeline and validation

MCP
→ Exposes the application's capabilities as tools for AI clients
```

MCP is therefore an integration layer rather than the component responsible for understanding the invoice.

---

## 👨‍💻 Author

**Aman Jain**

MCA (AI & ML) Graduate

GitHub: [AmanJain1011](https://github.com/AmanJain1011)

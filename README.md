# PDF Extractor with AI for Educational Resources

An AI-powered tool that automatically extracts structured metadata from educational PDF documents to facilitate cataloging and data entry into online survey systems.

## 📋 What It Does

This application uses **Claude AI (Sonnet 4)** to intelligently extract 18 structured fields from educational PDF documents, primarily focused on Spanish-language educational materials. It provides a user-friendly web interface for uploading PDFs, viewing extracted data, and copying information with one-click functionality.

### Key Features

- **Automated Field Extraction**: Extracts 18 different metadata fields from educational PDFs
- **AI-Powered Analysis**: Uses Anthropic's Claude AI for intelligent content understanding
- **Interactive Web Interface**: Built with Streamlit for easy PDF upload and data viewing
- **Copy-to-Clipboard**: One-click copying of extracted fields for easy data entry
- **Download Capability**: Downloads "Orientación de uso" (Usage Guidance) as text files
- **Spanish Language Focus**: Optimized for Spanish educational content

### Target Use Case

Designed for educational institutions (particularly in Latin America) that need to catalog and curate educational resources with detailed metadata. Streamlines the workflow for content curators processing educational materials.

## 🛠️ Tech Stack

**Language:** Python 3.x

**Core Dependencies:**
- **streamlit** - Web UI framework (serves both development and production interface)
- **PyPDF2** - PDF text extraction library
- **anthropic** - Anthropic's official Python SDK for Claude API integration
- **httpx** - HTTP client library for API requests

**AI Model:**
- **claude-sonnet-4-20250514** - Anthropic's Claude Sonnet 4 model

**External Services:**
- Anthropic Claude API for intelligent field extraction

## 📦 Installation & Setup

### Prerequisites

- Python 3.x
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure API Key

Create a Streamlit secrets file at `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "your-api-key-here"
```

Or set it as an environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## 🚀 Usage

### Running the Application

```bash
streamlit run DDC_streamlit.py
```

The application will open in your default web browser at `http://localhost:8501`

### User Workflow

1. **Upload PDF**: Click "Browse files" and select an educational PDF document
2. **Extract Title**: Title is automatically extracted from the filename
3. **Extract Fields**: Click the "Extraer campos con IA" (Extract fields with AI) button
4. **View Results**: Extracted information is displayed in 6 organized blocks
5. **Copy Data**: Use the copy buttons to copy individual fields to your clipboard
6. **Download**: Download the "Orientación de uso" section as a text file if needed

## 📂 Project Structure

```
extractor-pdf-ia/
├── DDC_streamlit.py       # Main application (596 lines)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Code Organization (DDC_streamlit.py)

The single-file application is organized into logical sections:

1. **Configuration** (Lines 1-24)
   - Import dependencies
   - Load Anthropic API key from Streamlit secrets

2. **UI Theme** (Lines 25-35)
   - Custom color palette (dark purple theme with 8 colors)
   - Primary: Dark purple (#1F0050)
   - Secondary: Cyan (#00E6DA)

3. **Utility Functions** (Lines 37-102)
   - `extract_text_from_pdf()` - Extracts raw text from PDF using PyPDF2
   - `extract_title_from_filename()` - Parses filename to extract title
   - `clean_nivel()` - Normalizes educational level data
   - `limpiar_orientacion()` - Cleans usage guidance text
   - `markdown_simple_a_html()` - Converts Markdown to HTML

4. **AI Integration** (Lines 103-215)
   - `extract_fields_with_ai()` - Main function that calls Claude API
   - Handles JSON parsing and error management
   - Processes all 18 structured fields

5. **UI Components** (Lines 217-399)
   - `create_copy_button_simple()` - Generates copy-to-clipboard JavaScript
   - `render_field()` - Displays field with copy button
   - `render_field_sin_boton()` - Displays field without button
   - `render_orientacion_markdown_con_descarga()` - Special rendering with download

6. **Main Interface** (Lines 400-594)
   - Streamlit page configuration
   - Custom CSS styling
   - Main UI layout with 6 information blocks

## 📝 Extracted Fields

The application extracts 18 fields organized into 6 blocks:

### Block 1: Basic Information
- **Título** (Title)
- **URL** (URL)
- **Tipo de contenido** (Content Type)

### Block 2: Educational Level
- **Ciclo** (Cycle/Level)
- **Grado** (Grade)
- **Área** (Area/Subject)
- **Descripción** (Description)

### Block 3: Curricular Information
- **Competencia** (Competency)
- **Capacidad** (Capacity/Skill)
- **Desempeño** (Performance/Learning Outcomes)

### Block 4: Pedagogical Guidance
- **Orientación de uso** (Usage Guidance) - with download capability

### Block 5: Technical Information
- **Tipo de recurso** (Resource Type)
- **Tipo de actividad** (Activity Type)
- **Idioma** (Language)
- **Etiquetas** (Tags)
- **Duración** (Duration)

### Block 6: Source Information
- **Autor** (Author)
- **Proveedor** (Provider)
- **Publicador** (Publisher)
- **Licencia** (License)

## 🔑 Key Functions

### Core Functions

- **`extract_text_from_pdf(pdf_file)`**
  - Extracts all text from uploaded PDF using PyPDF2
  - Returns concatenated text from all pages

- **`extract_fields_with_ai(pdf_text, title)`**
  - Main AI processing function
  - Sends PDF text and title to Claude API
  - Returns structured JSON with 18 extracted fields

- **`render_field(label, value, block_color)`**
  - Renders a field with label, value, and copy button
  - Uses custom styling with specified block color

- **`render_orientacion_markdown_con_descarga(orientacion, block_color)`**
  - Special rendering for usage guidance
  - Converts Markdown to HTML
  - Provides download button for text file

## 🎨 UI Features

- **Dark Theme**: Custom dark purple theme with cyan accents
- **Responsive Layout**: Clean, organized interface with 6 color-coded blocks
- **Copy Buttons**: JavaScript-powered copy-to-clipboard for all fields
- **Download Functionality**: Export usage guidance as .txt files
- **Error Handling**: Graceful error messages for API failures

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines if applicable]

## 📧 Contact

[Add contact information if applicable]

---

**Built with ❤️ using Streamlit and Claude AI**

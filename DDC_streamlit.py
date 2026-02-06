import streamlit as st
import PyPDF2
import anthropic
import httpx
import json
import streamlit.components.v1 as components
import re

# ============================================
# CONFIGURACIÓN - PEGA TU API KEY AQUÍ
# ============================================

try:                                                
    API_KEY = st.secrets["ANTHROPIC_API_KEY"]
    st.sidebar.success(f"✅ API Key cargada correctamente (longitud: {len(API_KEY)})")
except KeyError as e:
    API_KEY = ""
    st.sidebar.error(f"❌ Error: No se encontró la key en secrets: {e}")
    st.stop()
except Exception as e:
    API_KEY = ""
    st.sidebar.error(f"❌ Error inesperado: {e}")
    st.stop()

# ============================================
# PALETA DE COLORES
# ============================================
COLOR_PRIMARY = "#1F0050"      # Morado oscuro - principal
COLOR_SECONDARY = "#00E6DA"    # Cyan brillante - secundario
COLOR_ACCENT_1 = "#00849D"     # Azul oscuro
COLOR_ACCENT_2 = "#049A19"     # Verde oscuro
COLOR_SUCCESS = "#6AE081"      # Verde claro - éxito
COLOR_INFO = "#A23F97"         # Morado medio - info
COLOR_WARNING = "#F39107"      # Naranja - advertencias
COLOR_TEXT = "#FFFFFF"         # Blanco - texto sobre fondos oscuros

def extract_text_from_pdf(pdf_file):
    """Extrae todo el texto del PDF"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_title_from_filename(filename):
    """Extrae el título del nombre del archivo PDF"""
    name_without_ext = filename.replace('.pdf', '').replace('.PDF', '')
    
    if ' - ' in name_without_ext:
        title = name_without_ext.split(' - ')[0].strip()
    else:
        title = name_without_ext.strip()
    
    title = title.replace('(¿)', '¿').replace('(?)', '?')
    title = title.replace('(¡)', '¡').replace('(!)', '!')
    
    return title

def clean_nivel(ciclo_text):
    """Limpia el campo Nivel para mostrar solo Primaria o Secundaria"""
    if not ciclo_text:
        return "No encontrado"
    
    if "Primaria" in ciclo_text or "primaria" in ciclo_text:
        return "Primaria"
    elif "Secundaria" in ciclo_text or "secundaria" in ciclo_text:
        return "Secundaria"
    else:
        return ciclo_text

def limpiar_orientacion(texto):
    """Elimina el texto introductorio estándar de Orientación de uso"""
    if not texto:
        return texto
    
    # Texto a eliminar
    intro = "Estimado/a docente, usted es libre de utilizar este recurso educativo en los procesos pedagógicos y/o didácticos que usted considere pertinente, o siguiendo la siguiente propuesta:"
    
    # Si el texto comienza con la intro, eliminarlo
    if texto.strip().startswith(intro):
        texto_limpio = texto.replace(intro, "", 1).strip()
        return texto_limpio
    
    return texto

def markdown_simple_a_html(texto):
    """Convierte Markdown simple a HTML para que se copie limpio"""
    if not texto:
        return texto
    
    # Convertir **texto** a <strong>texto</strong>
    texto = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)
    
    # Convertir saltos de línea a <br>
    texto = texto.replace('\n', '<br>')
    
    # Convertir listas con * en viñetas (•)
    texto = re.sub(r'<br>\* ', '<br>• ', texto)
    texto = re.sub(r'^(\* )', r'• ', texto)
    
    return texto

def extract_fields_with_ai(pdf_text, api_key):
    """Extrae todos los campos usando Claude API"""
    client = anthropic.Anthropic(
        api_key=api_key,
        http_client=httpx.Client(verify=False)
    )
    
    prompt = f"""Analiza este texto de un PDF educativo y extrae EXACTAMENTE estos campos:

CAMPOS A EXTRAER:
1. Área
2. Ciclo
3. Grado
4. Descripción
5. Competencia
6. Capacidad
7. Desempeño
8. Orientación de uso
9. Tipo de recurso
10. Tipo de actividad
11. Idioma
12. Etiquetas
13. Duración
14. URL
15. Autor
16. Proveedor
17. Publicador
18. Licencia

REGLAS IMPORTANTES:
- IGNORA completamente el texto que dice: "PIP Mejoramiento de las oportunidades..."
- IGNORA números de código como "18107"

FORMATO ESPECIAL PARA "Orientación de uso":
Debes convertirlo a formato MARKDOWN con esta estructura:

**Subsección principal**

- Primer punto de lista
- Segundo punto de lista
  - Subpunto (con indentación de 2 espacios)
  - Otro subpunto

EJEMPLO de "Orientación de uso" en Markdown:
"Estimado/a docente, usted es libre de utilizar este recurso educativo en los procesos pedagógicos y/o didácticos que usted considere pertinente, o siguiendo la siguiente propuesta:

**Familiarización con el problema**

- Presentar la siguiente situación problemática: "El carpintero..."
- Plantear las siguientes preguntas para inducir el razonamiento y la acción:
  - ¿Cuál es la suma fija de los ángulos internos de cualquier triángulo?
  - ¿Qué pasa con los ángulos y lados de un triángulo si este es equilátero?

**Búsqueda y ejecución de estrategias**

- Visualizar el video: "Analizamos las propiedades..."
- Usar el problema de la ventana..."

FORMATO DE RESPUESTA:
Responde ÚNICAMENTE con un JSON válido (sin markdown, sin ```json):
{{
    "Área": "valor extraído",
    "Ciclo": "valor extraído",
    "Grado": "valor extraído",
    "Descripción": "valor extraído",
    "Competencia": "valor extraído",
    "Capacidad": "valor extraído",
    "Desempeño": "valor extraído",
    "Orientación de uso": "texto en formato MARKDOWN con **subsecciones** y - viñetas",
    "Tipo de recurso": "valor extraído",
    "Tipo de actividad": "valor extraído",
    "Idioma": "valor extraído",
    "Etiquetas": "valor extraído",
    "Duración": "valor extraído",
    "URL": "valor extraído",
    "Autor": "valor extraído",
    "Proveedor": "valor extraído",
    "Publicador": "valor extraído",
    "Licencia": "valor extraído"
}}

TEXTO DEL PDF:
{pdf_text}
"""
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        fields = json.loads(response_text)
        return fields
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Error al parsear JSON: {str(e)}")
        st.text("Respuesta de la API:")
        st.code(response_text)
        return None
    except anthropic.AuthenticationError as e:
        st.error(f"❌ Error de autenticación: Tu API Key no es válida")
        return None
    except Exception as e:
        st.error(f"❌ Error en la API: {str(e)}")
        return None

def create_copy_button_simple(text, field_id):
    """Botón con colores de la paleta y texto más grande"""
    safe_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
    
    html_code = f"""
    <div style="margin-top: 5px; margin-bottom: 10px;">
        <button onclick="copyText_{field_id}()" style="
            background-color: {COLOR_SECONDARY};
            color: {COLOR_PRIMARY};
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 3px 6px rgba(0,0,0,0.3);
            transition: all 0.3s;
        " onmouseover="this.style.backgroundColor='{COLOR_ACCENT_1}'; this.style.color='{COLOR_TEXT}';" 
           onmouseout="this.style.backgroundColor='{COLOR_SECONDARY}'; this.style.color='{COLOR_PRIMARY}';">
            📋 Copiar texto
        </button>
        
        <span id="status_{field_id}" style="
            margin-left: 15px;
            color: {COLOR_SUCCESS};
            font-size: 15px;
            display: none;
            font-weight: 600;
        ">✅ ¡Copiado!</span>
    </div>
    
    <script>
    function copyText_{field_id}() {{
        const text = '{safe_text}';
        
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        textarea.setSelectionRange(0, 99999);
        
        try {{
            const success = document.execCommand('copy');
            document.body.removeChild(textarea);
            
            if (success) {{
                const status = document.getElementById('status_{field_id}');
                status.style.display = 'inline';
                setTimeout(() => {{
                    status.style.display = 'none';
                }}, 3000);
            }} else {{
                alert('No se pudo copiar. Intenta seleccionar manualmente.');
            }}
        }} catch (err) {{
            document.body.removeChild(textarea);
            alert('Error al copiar. Por favor, selecciona el texto manualmente.');
        }}
    }}
    </script>
    """
    
    return html_code

def render_field(label, value, field_id, height=100):
    """Renderiza campo CON botón - texto más grande"""
    st.markdown(f"<h4 style='color: {COLOR_SECONDARY}; font-size: 20px;'>{label}</h4>", unsafe_allow_html=True)
    
    if not value:
        value = "No encontrado"
    
    if len(value) < 50:
        display_height = 60
    elif len(value) < 200:
        display_height = 100
    else:
        display_height = height
    
    st.markdown(
        f"""
        <style>
        textarea[aria-label*="ta_{field_id}"] {{
            font-size: 16px !important;
            line-height: 1.6 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.text_area(
        f"preview_{field_id}", 
        value, 
        height=display_height, 
        label_visibility="collapsed", 
        key=f"ta_{field_id}",
        disabled=True
    )
    
    button_html = create_copy_button_simple(value, field_id)
    components.html(button_html, height=70)

def render_field_sin_boton(label, value):
    """Renderiza campo SIN botón - solo info con texto más grande"""
    st.markdown(f"<h4 style='color: {COLOR_SECONDARY}; font-size: 20px;'>{label}</h4>", unsafe_allow_html=True)
    
    if not value:
        value = "No encontrado"
    
    st.markdown(
        f"""
        <div style="
            background-color: {COLOR_INFO};
            color: {COLOR_TEXT};
            padding: 15px;
            border-radius: 8px;
            font-size: 17px;
            line-height: 1.6;
            border-left: 5px solid {COLOR_SECONDARY};
        ">
        {value}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_orientacion_markdown_con_descarga(label, value):
    """Renderiza Orientación con HTML limpio para copiar sin asteriscos - FONDO BLANCO"""
    st.markdown(f"<h4 style='color: {COLOR_SECONDARY}; font-size: 20px;'>{label}</h4>", unsafe_allow_html=True)
    
    if not value:
        value = "No encontrado"
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(
            f"""
            <div style="
                background-color: {COLOR_INFO};
                color: {COLOR_TEXT};
                padding: 12px;
                border-radius: 6px;
                font-size: 15px;
            ">
            💡 <b>Opción 1:</b> Selecciona el texto de abajo y copia con Ctrl+C
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.download_button(
            label="📥 Descargar .txt",
            data=value,
            file_name="orientacion_de_uso.txt",
            mime="text/plain",
            help="Descarga el texto con formato"
        )
    
    # Convertir Markdown a HTML limpio
    value_html = markdown_simple_a_html(value)
    
    st.markdown(
        f"""<div style="
            background-color: #FFFFFF;
            color: #000000;
            padding: 25px;
            border-radius: 10px;
            border-left: 6px solid {COLOR_SECONDARY};
            margin: 15px 0;
            font-size: 17px;
            line-height: 1.8;
        ">
{value_html}
</div>""",
        unsafe_allow_html=True
    )
    
    st.caption("⬆️ Selecciona el texto y presiona Ctrl+C | O descarga el .txt")

# ============================================
# INTERFAZ STREAMLIT CON COLORES
# ============================================

st.set_page_config(
    page_title="Extractor PDF con IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    f"""
    <style>
    .stMarkdown p, .stMarkdown li {{
        font-size: 17px !important;
        line-height: 1.6 !important;
    }}
    
    .stAlert p {{
        font-size: 17px !important;
    }}
    
    h3 {{
        color: {COLOR_SECONDARY} !important;
        font-size: 24px !important;
    }}
    
    .stButton button {{
        background-color: {COLOR_ACCENT_2} !important;
        color: white !important;
        font-size: 18px !important;
        padding: 12px 30px !important;
        border-radius: 8px !important;
    }}
    
    .stButton button:hover {{
        background-color: {COLOR_SUCCESS} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🤖 Extractor de PDF con Inteligencia Artificial")
st.caption("Extrae campos de recursos educativos con precisión del 99% usando Claude AI")

with st.expander("ℹ️ Instrucciones de uso"):
    st.markdown("""
    ### Cómo usar esta herramienta:
    1. **Sube tu PDF** del recurso educativo
    2. **Haz clic en "Extraer campos con IA"**
    3. **Copia los campos** usando los botones donde estén disponibles
    4. **Para "Orientación de uso"**: Selecciona manualmente o descarga el archivo
    5. **Pega en tu encuesta web** con **Ctrl+V**
    """)

uploaded_file = st.file_uploader("📤 Sube el PDF del recurso educativo", type=['pdf'])

if uploaded_file:
    title = extract_title_from_filename(uploaded_file.name)
    full_text = extract_text_from_pdf(uploaded_file)
    
    st.success(f"✅ PDF cargado: **{uploaded_file.name}**")
    st.info(f"📄 Caracteres extraídos: {len(full_text)}")
    
    if st.button("🚀 Extraer campos con IA", type="primary", use_container_width=True):
        with st.spinner("🤖 Extrayendo con Inteligencia Artificial... ⏳"):
            fields = extract_fields_with_ai(full_text, API_KEY)
        
        if fields:
            st.success("✅ ¡Extracción completada con éxito!")
            st.session_state['fields'] = fields
            st.session_state['title'] = title

if 'fields' in st.session_state:
    fields = st.session_state['fields']
    title = st.session_state['title']
    
    st.markdown("---")
    st.markdown("## 📊 Campos Extraídos")
    
    # ============================================
    # BLOQUE 1
    # ============================================
    st.markdown("### 📑 Bloque 1")
    
    render_field("Título", title, "titulo", height=80)
    render_field("Enlace", fields.get("URL", ""), "url", height=80)
    render_field("Tipo de contenido", fields.get("Tipo de recurso", ""), "tipo_contenido", height=60)
    
    st.markdown(f"<h4 style='color: {COLOR_SECONDARY}; font-size: 20px;'>¿Requiere edición?</h4>", unsafe_allow_html=True)
    st.markdown(
        f"""<div style="background-color: {COLOR_ACCENT_2}; color: white; padding: 15px; border-radius: 8px; font-size: 17px;"><b>NO</b></div>""",
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # ============================================
    # BLOQUE 2 - Información Básica
    # ============================================
    st.markdown("### 📋 Bloque 2: Información Básica")
    
    nivel_limpio = clean_nivel(fields.get("Ciclo", ""))
    render_field_sin_boton("Nivel", nivel_limpio)
    render_field_sin_boton("Grado", fields.get("Grado", ""))
    render_field_sin_boton("Área", fields.get("Área", ""))
    render_field("Descripción del recurso educativo curado", fields.get("Descripción", ""), "descripcion", height=150)
    
    st.divider()
    
    # ============================================
    # BLOQUE 3 - Información Curricular
    # ============================================
    st.markdown("### 📚 Bloque 3: Información Curricular")
    
    render_field_sin_boton("Competencia", fields.get("Competencia", ""))
    render_field_sin_boton("Capacidad", fields.get("Capacidad", ""))
    render_field_sin_boton("Desempeño", fields.get("Desempeño", ""))
    
    st.divider()
    
    # ============================================
    # BLOQUE 4 - Orientación Pedagógica
    # ============================================
    st.markdown("### 📖 Bloque 4: Orientación Pedagógica")
    
    st.markdown(f"<h4 style='color: {COLOR_SECONDARY}; font-size: 20px;'>Requerimientos</h4>", unsafe_allow_html=True)
    st.markdown(
        f"""<div style="background-color: {COLOR_ACCENT_2}; color: white; padding: 15px; border-radius: 8px; font-size: 17px;"><b>TRABAJO EN GRUPOS</b></div>""",
        unsafe_allow_html=True
    )
    
    orientacion_limpia = limpiar_orientacion(fields.get("Orientación de uso", ""))
    render_orientacion_markdown_con_descarga("Orientación de uso", orientacion_limpia)
    
    st.divider()
    
    # ============================================
    # BLOQUE 5 - Información Técnica
    # ============================================
    st.markdown("### 🏷️ Bloque 5: Información Técnica")
    
    render_field_sin_boton("Tipo de Recurso", fields.get("Tipo de recurso", ""))
    
    st.markdown(f"<h4 style='color: {COLOR_SECONDARY}; font-size: 20px;'>Tipo de actividad</h4>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""<div style="background-color: {COLOR_WARNING}; color: white; padding: 15px; border-radius: 8px; font-size: 17px; text-align: center;"><b>VIDEO = Observar y Escuchar</b></div>""",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""<div style="background-color: {COLOR_ACCENT_1}; color: white; padding: 15px; border-radius: 8px; font-size: 17px; text-align: center;"><b>PDF = Leer y Reflexionar</b></div>""",
            unsafe_allow_html=True
        )
    
    st.markdown(f"<h4 style='color: {COLOR_SECONDARY}; font-size: 20px;'>Idioma</h4>", unsafe_allow_html=True)
    st.markdown(
        f"""<div style="background-color: {COLOR_ACCENT_2}; color: white; padding: 15px; border-radius: 8px; font-size: 17px;"><b>ESPAÑOL</b></div>""",
        unsafe_allow_html=True
    )
    
    render_field("Etiquetas", fields.get("Etiquetas", ""), "etiquetas", height=80)
    
    duracion_original = fields.get("Duración", "")
    duracion_formateada = duracion_original.replace(":", ".")
    render_field("Duración", duracion_formateada, "duracion", height=60)
    
    st.divider()
    
    # ============================================
    # BLOQUE 6 - Fuente
    # ============================================
    st.markdown("### 👤 Bloque 6: Fuente")
    
    render_field("Autor", fields.get("Autor", ""), "autor", height=60)
    render_field("Proveedor", fields.get("Proveedor", ""), "proveedor", height=60)
    render_field("Publicador", fields.get("Publicador", ""), "publicador", height=60)
    
    st.markdown(f"<h4 style='color: {COLOR_SECONDARY}; font-size: 20px;'>Licencia</h4>", unsafe_allow_html=True)
    st.markdown(
        f"""<div style="background-color: {COLOR_ACCENT_2}; color: white; padding: 15px; border-radius: 8px; font-size: 17px;"><b>Dominio Público</b></div>""",
        unsafe_allow_html=True
    )
    
    with st.expander("🔍 Debug"):
        st.json(fields)

else:

    st.info("👆 Sube un PDF y haz clic en 'Extraer campos con IA' para comenzar")



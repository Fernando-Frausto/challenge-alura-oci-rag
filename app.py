import streamlit as st

# --- 1. CONFIGURACIÓN DEL NÚCLEO (No Sidebar for clean look) ---
st.set_page_config(
    page_title="QroTech | AI Core v2.1",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. COLORES Y ESTILOS CORPORATIVOS ---
# Definimos los colores aquí para un mantenimiento fácil
BG_COLOR = "#070B19" # Deep Navy
CARD_BG_COLOR = "#0D111F" # Slightly lighter than BG
TEXT_COLOR = "#FAFAFA"
SUBTITLE_COLOR = "#8B949E"
CYAN_ACCENT = "#00F2FE"
CYAN_ALT = "#4FACFE"
BORDER_COLOR = "#1E293B"

# --- 3. CSS AVANZADO (Neo-Cyber Premium Look) ---
st.markdown(f"""
<style>
    /* Importar tipografía moderna de Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Space+Grotesk:wght@400;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* Fondo principal */
    .stApp {{
        background-color: {BG_COLOR}; 
    }}
    
    /* --- ENCABEZADO --- */
    .qrotech-title {{
        font-family: 'Space Grotesk', sans-serif;
        background: linear-gradient(90deg, {CYAN_ACCENT} 0%, {CYAN_ALT} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }}
    
    .qrotech-subtitle {{
        color: {SUBTITLE_COLOR};
        text-align: center;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 40px;
    }}

    /* --- TARJETAS DE ESTADO (Reemplazo de st.metric) --- */
    .status-container {{
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 30px;
    }}

    .status-card {{
        background-color: {CARD_BG_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 15px 20px;
        width: 100%;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}

    .status-card:hover {{
        border-color: {CYAN_ALT};
        box-shadow: 0 0 10px rgba(79, 172, 254, 0.3);
        transform: translateY(-2px);
    }}

    .status-label {{
        color: {SUBTITLE_COLOR};
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }}

    .status-value {{
        color: {CYAN_ACCENT};
        font-size: 1.3rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .status-icon-dot {{
        height: 12px;
        width: 12px;
        background-color: #00C853; /* Green */
        border-radius: 50%;
        display: inline-block;
    }}

    /* --- CHAT BUBBLES --- */
    [data-testid="stChatMessage"] {{
        background-color: transparent;
        margin-bottom: 15px;
    }}
    
    [data-testid="stChatMessageAsAssistant"] {{
        background-color: #0F172A;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid {BORDER_COLOR};
    }}
    
    [data-testid="stChatMessageAsAssistant"] p {{
        color: {TEXT_COLOR};
    }}

    /* Avatar del asistente */
    [data-testid="stChatMessageAvatar"] > div {{
        background-color: #0F172A;
        border-radius: 8px;
    }}

    /* --- INPUT TEXT --- */
    .stChatInputContainer {{
        border-radius: 12px;
        border: 1px solid {BORDER_COLOR};
        background-color: #0F172A;
        margin-top: 10px;
        transition: border-color 0.2s ease-in-out;
    }}
    
    .stChatInputContainer:focus-within {{
        border-color: {CYAN_ACCENT};
    }}

    /* Quitar línea superior por defecto */
    header {{visibility: hidden;}}
    .stDivider {{margin-bottom: 30px;}}

</style>
""", unsafe_allow_html=True)

# --- 4. ENCABEZADO PERSONALIZADO ---
st.markdown('<h1 class="qrotech-title">QroTech AI Core</h1>', unsafe_allow_html=True)
st.markdown('<p class="qrotech-subtitle">Motor de Análisis Documental RAG v2.1</p>', unsafe_allow_html=True)

# --- 5. DASHBOARD DE ESTADO (Custom HTML Cards - Fixes cut-off text) ---
st.markdown("""
<div class="status-container">
    <div class="status-card">
        <div class="status-label">Estado del Motor</div>
        <div class="status-value"><span class="status-icon-dot"></span> En línea</div>
    </div>
    <div class="status-card">
        <div class="status-label">Base Vectorial</div>
        <div class="status-value">⚡ FAISS Activa</div>
    </div>
    <div class="status-card">
        <div class="status-label">Documentos</div>
        <div class="status-value">📄 Manual de Sensores (v1)</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- 6. LÓGICA DEL CHAT REALIZADA (Base) ---
if "messages" not in st.session_state:
    # Usamos un mensaje técnico para dar contexto real
    st.session_state.messages = [
        {"role": "assistant", "content": "Sistemas inicializados. Conexión segura establecida con la base de datos de QroTech Data Systems.\n\n¿Qué componente técnico o especificación operativa del **Manual de Sensores de Impacto** deseas consultar hoy?"}
    ]

# Renderizar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. ENTRADA DEL USUARIO ---
# Mantenemos st.chat_input, el CSS personalizado se encarga de estilizarlo
if prompt := st.chat_input("Ingresa tu consulta técnica (ej. Rangos de voltaje)..."):
    
    # 1. Agregar pregunta del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generar respuesta del asistente (Aquí irá tu RAG real después)
    with st.chat_message("assistant"):
        # Mensaje de transición técnico
        with st.spinner("Realizando consulta vectorial en FAISS..."):
            # Simulamos respuesta
            respuesta = f"He recibido tu consulta sobre: **{prompt}**. Estamos procesando la documentación.\n\n*(Aquí conectaremos tu RAG real)*."
            st.markdown(respuesta)
        
    # 3. Guardar respuesta
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
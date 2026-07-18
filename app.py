import streamlit as st

# --- 1. CONFIGURACIÓN DEL NÚCLEO ---
st.set_page_config(
    page_title="QroTech | AI Core",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed" # Escondemos el menú lateral para ser únicos
)

# --- 2. CSS PARA UN DISEÑO ÚNICO (NEO-CYBER CORPORATIVO) ---
st.markdown("""
<style>
    /* Importar tipografía moderna de Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Fondo principal: Azul Medianoche Profundo */
    .stApp {
        background-color: #070B19; 
    }
    
    /* Título con efecto de luz (Gradiente Cyan a Verde) */
    .qrotech-title {
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    
    /* Subtítulo limpio */
    .qrotech-subtitle {
        color: #8B949E;
        text-align: center;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 30px;
    }

    /* Estilo de las métricas (Dashboard superior) */
    [data-testid="stMetricValue"] {
        color: #00F2FE !important;
        font-weight: 600;
    }
    [data-testid="stMetricLabel"] {
        color: #A0AEC0 !important;
    }
    
    /* Caja de texto (Chat Input) flotante y redondeada */
    .stChatInputContainer {
        border-radius: 20px;
        border: 1px solid #1E293B;
        background-color: #0F172A;
    }
    
    /* Quitar línea superior por defecto de Streamlit */
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. ENCABEZADO PERSONALIZADO ---
st.markdown('<h1 class="qrotech-title">QroTech AI Core</h1>', unsafe_allow_html=True)
st.markdown('<p class="qrotech-subtitle">Motor de Análisis Documental RAG v2.0</p>', unsafe_allow_html=True)

# --- 4. DASHBOARD DE ESTADO (Para darle un toque súper técnico) ---
col1, col2, col3 = st.columns(3)
col1.metric("Estado del Motor", "En línea 🟢")
col2.metric("Base Vectorial", "FAISS Activa ⚡")
col3.metric("Documentos", "1 (Manual_Sensores.pdf)")

st.divider()

# --- 5. LÓGICA DEL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Sistemas inicializados. Conexión segura establecida con la base de datos de QroTech. ¿Qué componente técnico deseas consultar hoy?"}
    ]

# Renderizar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. ENTRADA DEL USUARIO ---
if prompt := st.chat_input("Ingresa tu consulta técnica (ej. Especificaciones de voltaje)..."):
    
    # Imprimir pregunta
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Imprimir respuesta
    with st.chat_message("assistant"):
        # Aquí irá tu código RAG real
        respuesta = f"Procesando vectores para: **{prompt}**... \n\n*El sensor de impacto opera bajo un estándar de seguridad clase 4.*"
        st.markdown(respuesta)
        
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
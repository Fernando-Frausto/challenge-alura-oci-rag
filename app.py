import os
os.environ["GOOGLE_API_TRANSPORT"] = "rest"
import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS

# IMPORTANTE: Nuevas importaciones core modernas (adiós a langchain.chains)
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. CONFIGURACIÓN DEL NÚCLEO ---
st.set_page_config(
    page_title="QroTech | AI Core v2.1",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Validar y cargar API Key desde la bóveda secreta
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Error de Sistema: Clave GEMINI_API_KEY no encontrada en los secretos.")

# --- 2. COLORES Y ESTILOS CORPORATIVOS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Space+Grotesk:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #070B19; }
    
    .qrotech-title {
        font-family: 'Space Grotesk', sans-serif;
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    
    .qrotech-subtitle {
        color: #8B949E;
        text-align: center;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 40px;
    }

    .status-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 30px; }
    .status-card {
        background-color: #0D111F; border: 1px solid #1E293B; border-radius: 12px;
        padding: 15px 20px; width: 100%; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .status-label { color: #8B949E; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
    .status-value { color: #00F2FE; font-size: 1.3rem; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    .status-icon-dot { height: 12px; width: 12px; background-color: #00C853; border-radius: 50%; display: inline-block; }
    
    [data-testid="stChatMessageAsAssistant"] { background-color: #0F172A; border-radius: 12px; padding: 15px; border: 1px solid #1E293B; }
    [data-testid="stChatMessageAsAssistant"] p { color: #FAFAFA; }
    [data-testid="stChatMessageAvatar"] > div { background-color: #0F172A; border-radius: 8px; }
    
    .stChatInputContainer { border-radius: 12px; border: 1px solid #1E293B; background-color: #0F172A; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DEL MOTOR RAG (BACKEND) ---
def get_pdf_text(file_path):
    text = ""
    with open(file_path, "rb") as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return text_splitter.split_text(text)

def create_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",  # ¡Esta es la línea que cambiamos!
        google_api_key=st.secrets["GEMINI_API_KEY"],
        transport="rest"
    )
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store

def get_conversational_chain():
    prompt_template = """
    Eres el asistente técnico oficial de QroTech Data Systems.
    Responde a la consulta basándote ÚNICAMENTE en el contexto proporcionado del manual técnico.
    Si la respuesta no se encuentra en el contexto, responde "Esta información no se encuentra en la documentación actual del sistema", no inventes información.
    
    Contexto:
    {context}
    
    Pregunta:
    {question}
    
    Respuesta Técnica:
    """
    
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=0.3,
        google_api_key=st.secrets["GEMINI_API_KEY"],
        transport="rest"
    )
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Arquitectura LCEL: conecta prompt -> modelo -> texto puro (sin fallos de cadenas antiguas)
    return prompt | model | StrOutputParser()

# --- 4. AUTOMATIZACIÓN DEL AGENTE ---
PDF_PATH = "manual.pdf" 

if "vector_store" not in st.session_state:
    with st.spinner("Iniciando sistemas y cargando base de conocimiento..."):
        if os.path.exists(PDF_PATH):
            raw_text = get_pdf_text(PDF_PATH)
            text_chunks = get_text_chunks(raw_text)
            st.session_state.vector_store = create_vector_store(text_chunks)
            st.sidebar.success("✅ Base de conocimiento de QroTech cargada.")
        else:
            st.session_state.vector_store = None
            st.sidebar.error(f"⚠️ Error: No se encontró el archivo '{PDF_PATH}' en el servidor.")

# --- 5. ENCABEZADO Y DASHBOARD ---
st.markdown('<h1 class="qrotech-title">QroTech AI Core</h1>', unsafe_allow_html=True)
st.markdown('<p class="qrotech-subtitle">Motor de Análisis Documental RAG v2.1</p>', unsafe_allow_html=True)

estado_db = "⚡ FAISS Activa" if st.session_state.vector_store else "⚠️ Esperando PDF"
color_db = "#00C853" if st.session_state.vector_store else "#FACC15"

st.markdown(f"""
<div class="status-container">
    <div class="status-card">
        <div class="status-label">Estado del Motor</div>
        <div class="status-value"><span class="status-icon-dot"></span> En línea</div>
    </div>
    <div class="status-card">
        <div class="status-label">Base Vectorial</div>
        <div class="status-value" style="color: {color_db};">{estado_db}</div>
    </div>
    <div class="status-card">
        <div class="status-label">Procesador Lógico</div>
        <div class="status-value">🧠 Gemini 1.5</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- 6. LÓGICA DEL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Sistemas de QroTech inicializados.\n\nEl manual ha sido cargado en memoria de forma autónoma. ¿En qué te puedo ayudar?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ingresa tu consulta técnica..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.vector_store is None:
            st.warning("El motor RAG falló al cargar el manual local.")
        else:
            with st.spinner("Analizando documentación interna..."):
                docs = st.session_state.vector_store.similarity_search(prompt)
                
                # Extraemos el texto puro de los documentos encontrados
                context_text = "\n\n".join(doc.page_content for doc in docs)
                
                chain = get_conversational_chain()
                respuesta_final = chain.invoke({"context": context_text, "question": prompt})
                
                st.markdown(respuesta_final)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_final})
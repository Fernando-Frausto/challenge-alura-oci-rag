import streamlit as st
import os
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

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
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = pypdf.PdfReader(pdf)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

def get_text_chunks(text):
    # Reducimos los fragmentos a 500 caracteres para evitar el Timeout (504) de Google
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return text_splitter.split_text(text)

def create_vector_store(text_chunks):
    # Forzamos el protocolo REST para evadir el bloqueo de red de Streamlit
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        google_api_key=st.secrets["GEMINI_API_KEY"],
        task_type="retrieval_document",
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
    # Aplicamos el mismo puente REST al cerebro principal
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=0.3,
        google_api_key=st.secrets["GEMINI_API_KEY"],
        transport="rest"
    )
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)
# Inicializar Base Vectorial en la sesión
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

# --- 4. MENÚ LATERAL (CARGA DE DOCUMENTOS) ---
with st.sidebar:
    st.markdown("### 📂 Carga de Documentación")
    st.markdown("Sube el PDF para inyectarlo en la base vectorial.")
    pdf_docs = st.file_uploader("Selecciona archivos PDF", accept_multiple_files=True, type=["pdf"])
    
    if st.button("Procesar Datos en FAISS"):
        if pdf_docs:
            with st.spinner("Extrayendo texto y generando vectores..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                st.session_state.vector_store = create_vector_store(text_chunks)
                st.success("✅ Base vectorial actualizada y lista.")
        else:
            st.warning("⚠️ Sube un documento primero.")

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
        {"role": "assistant", "content": "Sistemas de QroTech inicializados.\n\nPor favor, abre el menú lateral (arriba a la izquierda ＞), sube tu manual en PDF y presiona procesar. Luego podrás hacerme consultas técnicas."}
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
            st.warning("El motor RAG no tiene contexto. Por favor, sube y procesa un PDF en el menú lateral.")
        else:
            with st.spinner("Analizando documentación interna..."):
                docs = st.session_state.vector_store.similarity_search(prompt)
                chain = get_conversational_chain()
                response = chain({"input_documents": docs, "question": prompt}, return_only_outputs=True)
                respuesta_final = response["output_text"]
                st.markdown(respuesta_final)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_final})
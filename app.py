import os
# Forzamos la conexión REST desde el inicio para evitar los bloqueos (Error 504)
os.environ["GOOGLE_API_TRANSPORT"] = "rest"

import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. CONFIGURACIÓN DEL NÚCLEO ---
st.set_page_config(
    page_title="QroTech | AI Core",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if "GEMINI_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Error: Clave GEMINI_API_KEY no encontrada.")

# --- 2. ESTILOS VISUALES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Space+Grotesk:wght@700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #070B19; }
    .qrotech-title { font-family: 'Space Grotesk', sans-serif; background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem; text-align: center; margin-bottom: 0px; }
    .qrotech-subtitle { color: #8B949E; text-align: center; margin-bottom: 30px; }
    .status-card { background-color: #0D111F; border: 1px solid #1E293B; border-radius: 12px; padding: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES RAG ---
def get_pdf_text(file_path):
    text = ""
    with open(file_path, "rb") as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

def create_vector_store(text_chunks):
    # Usamos la versión estable del modelo con el candado REST obligatorio
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=st.secrets["GEMINI_API_KEY"],
        transport="rest"  # <-- Esto es lo que olvidé ponerte
    )
    return FAISS.from_texts(text_chunks, embedding=embeddings)

# --- 4. ARRANQUE AUTÓNOMO ---
PDF_PATH = "manual.pdf" 

if "vector_store" not in st.session_state:
    with st.spinner("Inicializando motor de conocimiento..."):
        if os.path.exists(PDF_PATH):
            raw_text = get_pdf_text(PDF_PATH)
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_text(raw_text)
            st.session_state.vector_store = create_vector_store(chunks)
            st.sidebar.success("✅ Sistema Listo")
        else:
            st.session_state.vector_store = None
            st.sidebar.error("⚠️ Archivo manual.pdf no encontrado.")

# --- 5. INTERFAZ ---
st.markdown('<h1 class="qrotech-title">QroTech AI Core</h1>', unsafe_allow_html=True)
st.markdown('<p class="qrotech-subtitle">Sistema Autónomo de Análisis Documental</p>', unsafe_allow_html=True)

if st.session_state.vector_store:
    st.markdown('<div class="status-card" style="color:#00C853; border-color:#00C853;">✅ Base Vectorial FAISS Activa y Conectada</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-card" style="color:#FACC15;">⚠️ Esperando documento base</div>', unsafe_allow_html=True)

st.divider()

# --- 6. MOTOR DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistemas inicializados. ¿En qué te puedo ayudar con el manual de QroTech?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu consulta técnica..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not st.session_state.vector_store:
            st.warning("El sistema no tiene contexto cargado.")
        else:
            with st.spinner("Analizando manual..."):
                # Búsqueda en FAISS
                docs = st.session_state.vector_store.similarity_search(prompt)
                context_text = "\n\n".join(doc.page_content for doc in docs)
                
                # Configuración del LLM
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash", 
                    temperature=0.3,
                    google_api_key=st.secrets["GEMINI_API_KEY"],
                    transport="rest"  # <-- Candado REST también para el chat
                )
                
                # Prompt estricto
                template = """
                Eres el asistente técnico de QroTech Data Systems.
                Responde ÚNICAMENTE basándote en el siguiente contexto. Si no está ahí, di "No tengo información sobre eso".
                
                Contexto: {context}
                
                Pregunta: {question}
                """
                prompt_template = PromptTemplate.from_template(template)
                
                # Ejecución de la cadena (LCEL)
                chain = prompt_template | llm | StrOutputParser()
                respuesta = chain.invoke({"context": context_text, "question": prompt})
                
                st.markdown(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
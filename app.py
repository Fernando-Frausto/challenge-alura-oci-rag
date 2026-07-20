import os
# Forzamos la conexión REST desde el inicio para evitar bloqueos en la nube
os.environ["GOOGLE_API_TRANSPORT"] = "rest"

import streamlit as st
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

# Cargamos la llave desde los secretos de Streamlit
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Error: Clave GEMINI_API_KEY no encontrada en los secretos de Streamlit.")

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

# --- 3. ARRANQUE AUTÓNOMO CON MEMORIA PRE-CARGADA ---
if "vector_store" not in st.session_state:
    with st.spinner("Conectando memoria neuronal..."):
        # Buscamos la carpeta faiss_index que generaste en Colab
        if os.path.exists("faiss_index"):
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001", # El modelo que comprobaste que funciona
                google_api_key=st.secrets["GEMINI_API_KEY"],
                transport="rest"
            )
            # allow_dangerous_deserialization permite leer el archivo que tú mismo creaste
            st.session_state.vector_store = FAISS.load_local(
                "faiss_index", embeddings, allow_dangerous_deserialization=True
            )
            st.sidebar.success("✅ Memoria de QroTech Conectada")
        else:
            st.session_state.vector_store = None
            st.sidebar.error("⚠️ Error: Carpeta 'faiss_index' no encontrada en el repositorio.")

# --- 4. INTERFAZ ---
st.markdown('<h1 class="qrotech-title">QroTech AI Core</h1>', unsafe_allow_html=True)
st.markdown('<p class="qrotech-subtitle">Sistema Autónomo de Análisis Documental</p>', unsafe_allow_html=True)

if st.session_state.vector_store:
    st.markdown('<div class="status-card" style="color:#00C853; border-color:#00C853;">✅ Base Vectorial FAISS Activa y Conectada</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-card" style="color:#FACC15;">⚠️ Esperando memoria base</div>', unsafe_allow_html=True)

st.divider()

# --- 5. MOTOR DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistemas inicializados. La base de conocimiento está conectada. ¿En qué te puedo ayudar con el manual de QroTech?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu consulta técnica..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not st.session_state.vector_store:
            st.warning("El sistema no tiene contexto cargado. Falta la carpeta faiss_index.")
        else:
            with st.spinner("Analizando manual..."):
                # Búsqueda en la base de datos local FAISS
                docs = st.session_state.vector_store.similarity_search(prompt)
                context_text = "\n\n".join(doc.page_content for doc in docs)
                
                # Configuración del LLM
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash", 
                    temperature=0.3,
                    google_api_key=st.secrets["GEMINI_API_KEY"],
                    transport="rest"
                )
                
                # Arquitectura moderna LCEL
                template = """
                Eres el asistente técnico de QroTech Data Systems.
                Responde ÚNICAMENTE basándote en el siguiente contexto. Si no está ahí, di "No tengo información sobre eso".
                
                Contexto: {context}
                
                Pregunta: {question}
                """
                prompt_template = PromptTemplate.from_template(template)
                
                chain = prompt_template | llm | StrOutputParser()
                respuesta = chain.invoke({"context": context_text, "question": prompt})
                
                st.markdown(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
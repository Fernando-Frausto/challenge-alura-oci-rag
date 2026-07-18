import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Variables de configuracion hacia LM Studio local
url_local = "http://127.0.0.1:1234/v1"
llave_simulada = "lm-studio"
ruta_pdf = "Manual_QroTech.pdf"

print("Iniciando sistema RAG de QroTech...")

# 2. Ingesta del PDF que creaste manualmente
cargador_pdf = PyPDFLoader(file_path=ruta_pdf)
documentos = cargador_pdf.load_and_split()
print(f"-> PDF leido exitosamente. Dividido en {len(documentos)} fragmentos.")

# 3. Vectorizacion Matematica
# (La primera vez tardara unos minutos descargando el modelo a tu RAM)
modelo_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
base_vectorial = FAISS.from_documents(documentos, modelo_embeddings)
print("-> Base de datos vectorial FAISS creada en memoria.")

# 4. Orquestacion del LLM Local
llm = ChatOpenAI(base_url=url_local, api_key=llave_simulada, temperature=0.1)

plantilla_prompt = ChatPromptTemplate.from_template("""
Eres el agente de Inteligencia Artificial de la empresa QroTech Data Systems.
Responde la pregunta basándote EXCLUSIVAMENTE en el siguiente contexto.
Si la respuesta no está, di: "No cuento con esa información".

Contexto: 
{context}

Pregunta del usuario: {input}
""")

cadena_documentos = create_stuff_documents_chain(llm, plantilla_prompt)
agente_rag = create_retrieval_chain(base_vectorial.as_retriever(search_kwargs={"k": 2}), cadena_documentos)

print("\n--- SISTEMA LISTO ---")

# 5. Prueba de inferencia
pregunta = "¿Qué pasa si rechazo una entrega porque el sensor de impacto está en rojo?"
print(f"\nUsuario: {pregunta}")

# Ejecutamos la consulta
respuesta = agente_rag.invoke({"input": pregunta})
print(f"\nAgente QroTech: {respuesta['answer']}")
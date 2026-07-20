import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Configuración de tu API Key (Para demostración en el repositorio)
# Nota: En producción, esto debe ocultarse en variables de entorno.
os.environ["GOOGLE_API_KEY"] = "TU_API_KEY_AQUI" 

def crear_base_vectorial():
    print("1. Leyendo el documento PDF...")
    # Asegúrate de que el archivo manual.pdf esté en la misma carpeta
    pdf_reader = PdfReader("manual.pdf")
    texto_completo = ""
    for pagina in pdf_reader.pages:
        texto_completo += pagina.extract_text()
        
    print("2. Dividiendo el texto en fragmentos (Chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    fragmentos = text_splitter.split_text(texto_completo)
    
    print("3. Generando Embeddings con Google Gemini...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    print("4. Creando e indexando la base de datos FAISS...")
    vector_store = FAISS.from_texts(fragmentos, embedding=embeddings)
    
    print("5. Guardando la memoria localmente...")
    vector_store.save_local("faiss_index")
    print("¡Éxito! Base vectorial 'faiss_index' generada correctamente.")

if __name__ == "__main__":
    crear_base_vectorial()
# 🚀 QroTech AI Agent: Arquitectura RAG Corporativa

Este proyecto es una implementación completa de un agente de Inteligencia Artificial utilizando una arquitectura **RAG (Retrieval-Augmented Generation)**. El sistema ingesta un manual corporativo de 6 páginas, vectoriza su contenido y responde consultas precisas basándose exclusivamente en las políticas, métricas de ventas y SLAs de la empresa, evitando alucinaciones.

Desarrollado como parte del desafío final de despliegue de Alura Latam.

---

## 🏗️ Stack Tecnológico y Arquitectura

El flujo de procesamiento local se divide en las siguientes capas:

1. **Capa de Ingesta (`PyPDFLoader`):** Extracción del texto puro del manual corporativo (PDF) y división en fragmentos (chunks) manejables.
2. **Capa de Vectorización (`HuggingFaceEmbeddings`):** Transformación del texto a tensores matemáticos utilizando el modelo local `all-MiniLM-L6-v2`.
3. **Base de Datos Vectorial (`FAISS`):** Indexación en memoria RAM para búsquedas de similitud semántica ultrarrápidas.
4. **Orquestación RAG (`LangChain Classic`):** Ensamblaje de la cadena de recuperación y el prompt sistémico.
5. **Capa de Inferencia (LLM Local):** Interconexión vía API con **LM Studio** ejecutando modelos ligeros (ej. Gemma / Llama-3) en el puerto local `1234`.

---

## 🧠 Ejemplo de Interacción (Q&A)

El agente está configurado para responder basándose estrictamente en el documento.

> **Usuario:** ¿Qué pasa si rechazo una entrega porque el sensor de impacto está en rojo?
> 
> **Agente QroTech:** El cliente tiene la responsabilidad de rechazar la recepción del bulto inmediatamente con el transportista y no firmar ningún documento de conformidad. QroTech se compromete a cumplir con los términos contractuales...

---

## ⚙️ Instrucciones de Ejecución Local

Para replicar este entorno, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/challenge-alura-oci-rag.git](https://github.com/TU_USUARIO/challenge-alura-oci-rag.git)
   cd challenge-alura-oci-rag
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_DB_PATH = "ai/vector_store.pkl"

def ask_docs(question, k=3):
    if not os.path.exists(VECTOR_DB_PATH):
        return "📄 No documents indexed yet. Please upload a PDF."

    with open(VECTOR_DB_PATH, "rb") as f:
        index, chunks = pickle.load(f)

    q_embedding = MODEL.encode([question])
    distances, indices = index.search(q_embedding, k)

    results = []
    for idx in indices[0]:
        if idx < len(chunks):
            results.append(chunks[idx])

    if not results:
        return "📄 No relevant information found in the documents."

    return "📄 From college documents:\n\n" + "\n---\n".join(results)

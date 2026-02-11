from sentence_transformers import SentenceTransformer
import faiss
import pickle

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_DB_PATH = "ai/vector_store.pkl"

def create_embeddings(chunks):
    embeddings = MODEL.encode(chunks)

    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(embeddings)

    with open(VECTOR_DB_PATH, "wb") as f:
        pickle.dump((index, chunks), f)

import chromadb
from chromadb.utils import embedding_functions

collection = None

def get_collection():
    """Singleton function to manage the ChromaDB collection."""
    global collection
    if collection is None:
        print("--- Establishing Connection to VectorDB ---")
        embedding_model = embedding_functions.DefaultEmbeddingFunction()
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(
            name="f1_knowledge", 
            embedding_function=embedding_model
        )
    return collection

def add_document_to_db(chunks, doc_name):
    """Standardized storage logic."""
    collection = get_collection()
    ids = [f"{doc_name}_{i}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=[{"source": doc_name} for _ in chunks]
    )

""" this function is used in main.py to retrieve relevant context for question generation and evaluation.
def get_relevant_context(query, n_results=2):
    Retrieves context from the existing database.
    results = collection.query(query_texts=[query], n_results=n_results)
    return " ".join(results['documents'][0])
"""
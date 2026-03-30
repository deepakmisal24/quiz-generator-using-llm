import chromadb
from chromadb.utils import embedding_functions

_collection = None

def get_collection():
    global _collection
    if _collection is None:
        embedding_model = embedding_functions.DefaultEmbeddingFunction()
        client = chromadb.PersistentClient(path="./chroma_db")
        _collection = client.get_or_create_collection(
            name="f1_knowledge", 
            embedding_function=embedding_model
        )
    return _collection

def add_document_to_db(chunks, doc_name):
    print(f"--- Adding document to DB: {doc_name} with {len(chunks)} chunks ---")
    collection = get_collection()
    
    existing_ids = collection.get()['ids']
    if existing_ids:
        collection.delete(ids=existing_ids)
        
    ids = [f"{doc_name}_{i}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=[{"source": doc_name} for _ in chunks]
    )
    print(f"--- Added {len(chunks)} chunks to the database from {doc_name} ---")
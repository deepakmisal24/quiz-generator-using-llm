import fitz  # PyMuPDF
from vector_engine import add_document_to_db

def process_pdf(file_path):
    """ETL: Extract, Transform, and Load into VectorDB."""
    print(f"--- Processing {file_path} ---")
    
    # 1. Extract (Extract)
    with fitz.open(file_path) as doc:
        raw_text = " ".join([page.get_text() for page in doc])
    
    # 2. Chunk (Transform)
    # We split by 1000 characters to keep context meaningful
    chunks = [raw_text[i:i+1000] for i in range(0, len(raw_text), 1000)]
    
    # 3. Store in ChromaDB (Load)
    add_document_to_db(chunks, file_path)
    print(f"Successfully ingested {len(chunks)} chunks into ChromaDB.")

if __name__ == "__main__":
    
    process_pdf("Formula1_Complete_Guide.pdf")
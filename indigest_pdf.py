import fitz  # PyMuPDF
from vector_engine import add_document_to_db

def process_pdf(file_path):
    """Accepts any file path provided by the UI/API."""
    print(f"--- Extracting text from: {file_path} ---")
    with fitz.open(file_path) as doc:
        raw_text = " ".join([page.get_text() for page in doc])
    
    # Create chunks
    chunks = [raw_text[i:i+1000] for i in range(0, len(raw_text), 1000)]
    
    # Store in DB
    add_document_to_db(chunks, file_path)
    print(f"--- Finished processing: {file_path} ---")
    return True
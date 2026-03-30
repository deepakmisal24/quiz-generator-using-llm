import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

# Import your synchronized backend modules
from indigest_pdf import process_pdf
from generate_quiz import generate_and_save_quiz
from main import evaluate_answer, get_text_from_ids, answer_custom_question

app = FastAPI(title="AI Quiz API")

# Ensure a directory exists for uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Data model for the evaluation request
class EvalRequest(BaseModel):
    question: str
    user_answer: str
    correct_answer: str
    context_used: list # List of ChromaDB IDs

@app.post("/upload-and-process")
async def handle_upload(file: UploadFile = File(...)):
    """
    THE PIPELINE:
    1. Saves the PDF locally.
    2. Calls indigest_pdf.py to extract and store text.
    3. Calls generate_quiz.py to create 10 new questions.
    """
    try:
        # 1. Save the file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 2. Extract & Ingest into VectorDB
        process_pdf(file_path)

        # 3. Generate the Quiz Bank
        quiz_data = generate_and_save_quiz(count=10)

        return {
            "status": "success", 
            "message": f"Processed {file.filename} and generated {len(quiz_data)} questions."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quiz-bank")
def get_quiz():
    """Retrieves the currently generated quiz from the JSON file."""
    try:
        with open('quiz_bank.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No quiz generated yet.")

@app.post("/evaluate")
def evaluate(data: EvalRequest):
    """
    EVALUATION PIPELINE:
    1. Fetches the original PDF text using IDs.
    2. Uses the LLM to explain the answer based on that text.
    """
    # Fetch the 'Source of Truth' from the database
    actual_context = get_text_from_ids(data.context_used)
    
    # Run the evaluation logic
    verdict, explanation = evaluate_answer(
        data.question, 
        data.user_answer, 
        data.correct_answer, 
        actual_context
    )
    
    return {"verdict": verdict, "explanation": explanation}

class CustomQueryRequest(BaseModel):
    query: str

@app.post("/ask-custom")
def ask_custom(data: CustomQueryRequest):
    answer = answer_custom_question(data.query)
    return {"answer": answer}
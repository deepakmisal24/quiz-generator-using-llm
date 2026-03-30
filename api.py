from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from main import get_text_from_ids, evaluate_answer # Import from your logic file

app = FastAPI(title="F1 Quiz Engine")

class QuizRequest(BaseModel):
    question: str
    user_answer: str
    correct_answer: str
    context_used: list # This will be the list of IDs

@app.get("/quiz-data")
def get_quiz_bank():
    try:
        with open('quiz_bank.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="quiz_bank.json not found. Run generate_quiz.py.")

@app.post("/verify")
def verify(data: QuizRequest):
    # 1. Rehydrate IDs into actual text
    actual_context = get_text_from_ids(data.context_used)
    
    # 2. Evaluate
    verdict, explanation = evaluate_answer(
        data.question, 
        data.user_answer, 
        data.correct_answer, 
        actual_context
    )
    
    return {"verdict": verdict, "explanation": explanation}
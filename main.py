import ollama
import json
from vector_engine import get_collection
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="F1 Quiz API")

# Data Models
class AnswerRequest(BaseModel):
    question: str
    user_answer: str
    correct_answer: str
    context_refs: list

def get_text_from_ids(chunk_ids):
    """Retrieves the actual text from ChromaDB using the stored Reference IDs."""
    collection = get_collection()
    results = collection.get(ids=chunk_ids)
    return " ".join(results['documents'])

@app.get("/get-quiz")
def get_quiz():
    try:
        with open('quiz_bank.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz bank not found. Run generate_quiz.py.")

@app.post("/evaluate")
def evaluate_answer(question, user_answer, correct_answer, selected_context):
    """Evaluation: Checks the user's input using the LLM for feedback."""
    print("--- Evaluating your Answer ---")
    is_correct = user_answer.upper() == correct_answer.upper()
    verdict = "CORRECT" if is_correct else "INCORRECT"
    prompt = f"""
    STRICT COMPARISON TASK:
    1. Target Letter: {correct_answer}
    2. User Provided: {user_answer}
    
    COMPARE: Does {user_answer} match {correct_answer}?
    
    Provide feedback in this format:
    VERDICT: {verdict}
    EXPLANATION: [Provide a brief explanation (max 2 sentences) that cites the specific fact from the 
    {selected_context} above that proves why {correct_answer} is the right answer.]
    """

    system_instruction = (
        "You are a strict grading logic assistant. "
        "Compare the 'User Provided' letter to the 'Target Letter'. "
        "If they are different letters, the verdict MUST be 'INCORRECT'. "
        "Be concise and do not hallucinate."
        "You are a factual auditor. Your only job is to explain a quiz answer "
        "using ONLY the provided context. Do not use outside knowledge. "
        "If the information is not in the context, say 'Information not available in text'."
    )
    response = ollama.generate(model='gemma3:1b', system=system_instruction, prompt=prompt)
    return verdict,response['response']


def run_quiz():
    try:
        with open('quiz_bank.json', 'r') as f:
            quiz_bank = json.load(f)
    except FileNotFoundError:
        print("Error: No quiz bank found. Run generate_quiz.py first.")
        return

    score = 0
    for i, item in enumerate(quiz_bank):
        print(f"\n--- Question {i+1} of {len(quiz_bank)} ---")
        print(item['question'])
        for idx, opt in enumerate(item['options']):
            print(f"{chr(65+idx)}) {opt}")
        
        user_choice = ""
        while user_choice not in ['A', 'B', 'C', 'D']:
            user_choice = input("\nYour Answer (A, B, C, D): ").upper()
        context_used = get_text_from_ids(item['context_used'])
        verdict, feedback = evaluate_answer(item['question'], user_choice, item['correct_answer'], context_used)
        
        if verdict == "CORRECT":
            score += 1
            print("✅ CORRECT!")
        else:
            print(f"❌ INCORRECT. The right answer was {item['correct_answer']}.")
        
        print(f"Feedback: {feedback}")
        print(f"Current Score: {score}/{i+1}")
        input("\nPress Enter for the next question...")


if __name__ == "__main__":
    run_quiz()

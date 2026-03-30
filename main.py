import ollama
import json
from vector_engine import get_collection

def get_text_from_ids(chunk_ids):
    """Retrieves original text from ChromaDB using Reference IDs."""
    collection = get_collection()
    # IDs are stored as a list in the JSON; we fetch them all at once
    results = collection.get(ids=chunk_ids)
    return " ".join(results['documents'])

def evaluate_answer(question, user_answer, correct_answer, context):
    """Refined Evaluation: Checks logic and provides context-grounded feedback."""
    # Reliable Python check for the verdict
    is_correct = user_answer.upper() == correct_answer.upper()
    verdict = "CORRECT" if is_correct else "INCORRECT"
    
    system_instruction = (
        "You are a strict factual auditor. Explain quiz answers using ONLY the provided context. "
        "Do not use outside knowledge. Be concise (max 2 sentences)."
    )

    prompt = f"""
    CONTEXT FROM PDF:
    {context}

    QUESTION: {question}
    USER CHOSE: {user_answer}
    CORRECT OPTION: {correct_answer}

    TASK:
    The user was {verdict}. Explain why {correct_answer} is the correct choice based on the PDF context above.
    """

    response = ollama.generate(model='gemma3:1b', system=system_instruction, prompt=prompt)
    return verdict, response['response']

# We keep this for quick terminal testing, but the real app will use the API
if __name__ == "__main__":
    print("Logic Layer Loaded. To run the full app, start api.py and app.py.")
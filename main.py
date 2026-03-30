import ollama
from vector_engine import get_collection

def get_text_from_ids(chunk_ids):
    collection = get_collection()
    results = collection.get(ids=chunk_ids)
    return " ".join(results['documents'])

def evaluate_answer(question, user_answer, correct_answer, context):
    """Provides the AI explanation for the UI."""
    print(f"--- Evaluating Answer: User chose for the question:- {question} ---")
    is_correct = user_answer.upper() == correct_answer.upper()
    verdict = "CORRECT" if is_correct else "INCORRECT"
    
    prompt = f"""
    CONTEXT FROM PDF:
    {context}

    QUESTION: {question}
    USER CHOSE: {user_answer}
    CORRECT OPTION: {correct_answer}

    TASK:
    The user was {verdict}. Explain why {correct_answer} is the correct choice based on the PDF context above."""
    system_instruction = (
        "You are a strict factual auditor. Explain quiz answers using ONLY the provided context. "
        "Do not use outside knowledge. Be concise (max 2 sentences)."
    )
    response = ollama.generate(model='deepseek-r1:1.5b', prompt=prompt,system=system_instruction)
    return verdict, response['response']

def answer_custom_question(user_query):
    """Classic RAG: Search the DB and answer based ONLY on the PDF."""
    print(f"--- Received Custom Query: {user_query} ---")
    collection = get_collection()
    
    # 1. Search for the 3 most relevant chunks
    results = collection.query(
        query_texts=[user_query],
        n_results=3
    )
    
    context = " ".join(results['documents'][0])
    
    # 2. Ask the LLM to answer using the context
    system_instruction = (
        "You are a expert. Answer the question using ONLY the provided context. "
        "If the answer is not in the context, strictly say 'Information not available in the uploaded content'."
    )
    
    prompt = f"CONTEXT FROM PDF:\n{context}\n\nUSER QUESTION: {user_query}"
    
    response = ollama.generate(model='qwen2.5:3b', system=system_instruction, prompt=prompt)
    return response['response']
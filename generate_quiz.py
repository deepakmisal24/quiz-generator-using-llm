import json
import random
import ollama
from vector_engine import get_collection

def generate_and_save_quiz(count=10):
    collection = get_collection()
    all_data = collection.get()
    docs = all_data['documents']
    ids = all_data['ids']
    
    if not docs:
        return []

    quiz_bank = []
    print(f"--- Generating {count} quiz questions from {len(docs)} document chunks ---")
    while len(quiz_bank) < count:
        indices = random.sample(range(len(docs)), min(len(docs), 2))
        selected_context = " ".join([docs[i] for i in indices])
        selected_ids = [ids[i] for i in indices]

        prompt = f"""
        ### CONTEXT:
        {selected_context}

        ### TASK:
        Generate one Multiple Choice Question (MCQ) from the context above[cite: 20].

        ### CONSTRAINTS:
        - The question must be factually supported by the text[cite: 20].
        - Ensure 'options' contains exactly 4 choices.
        - The 'correct_answer' key must contain ONLY the letter (A, B, C, or D) that corresponds to the correct option.
        - Avoid 'All of the above' or 'None of the above' style answers to prevent overlap.

        ### EXPECTED JSON FORMAT:
        {{
        "question": "Your question here?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "A"
        }}
        """
        system_instruction = (
            "You are a professional exam coordinator. Your task is to generate high-quality, "
            "unambiguous Multiple Choice Questions based ONLY on the provided text[cite: 20]. "
            "STRICT RULES:\n"
            "1. Only ONE option must be correct.\n"
            "2. Distractors (wrong options) must be plausible but distinct; they must NOT overlap in meaning with the correct answer.\n"
            "3. Return response in VALID JSON only.\n"
            "4. Keys: 'question' (string), 'options' (list of 4 distinct strings), 'correct_answer' (single letter A, B, C, or D)."
        )

        try:
            response = ollama.generate(model='qwen2.5:3b', prompt=prompt, system=system_instruction, format="json")
            data = json.loads(response['response'])
            data['context_used'] = selected_ids
            quiz_bank.append(data)
        except:
            continue

    with open('quiz_bank.json', 'w') as f:
        json.dump(quiz_bank, f, indent=4)
    print(f"--- Quiz generation complete. {len(quiz_bank)} questions saved to quiz_bank.json ---")
    
    return quiz_bank
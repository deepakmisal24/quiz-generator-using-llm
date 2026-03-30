import json
import random
import ollama
from vector_engine import get_collection

def generate_and_save_quiz(count=10):
    print(f"--- Generating {count} Questions ---")
    collection=get_collection()
    all_data = collection.get()
    docs = all_data['documents']
    ids = all_data['ids']
    
    if not docs:
        print("No data found in VectorDB. Run ingest.py first.")
        return

    quiz_bank = []
    
    # We loop to ensure we get exactly 10 questions
    while len(quiz_bank) < count:
        indices = random.sample(range(len(docs)), min(len(docs), 2))
        selected_context = " ".join([docs[i] for i in indices])
        selected_ids = [ids[i] for i in indices]

        system_instruction = (
            "You are a professional exam coordinator. Your task is to generate high-quality, "
            "unambiguous Multiple Choice Questions based ONLY on the provided text[cite: 20]. "
            "STRICT RULES:\n"
            "1. Only ONE option must be correct.\n"
            "2. Distractors (wrong options) must be plausible but distinct; they must NOT overlap in meaning with the correct answer.\n"
            "3. Return response in VALID JSON only.\n"
            "4. Keys: 'question' (string), 'options' (list of 4 distinct strings), 'correct_answer' (single letter A, B, C, or D)."
        )
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

        try:
            response = ollama.generate(model='gemma3:1b', system=system_instruction, prompt=prompt, format="json")
            data = json.loads(response['response'])
            
            
            # ADD THE CONTEXT HERE
            data['context_used'] = selected_ids
            if data['question'] not in [q['question'] for q in quiz_bank]:
                quiz_bank.append(data)
        except Exception as e:
            print(f"Generation error, retrying... {e}")

    with open('quiz_bank.json', 'w') as f:
        json.dump(quiz_bank, f, indent=4)
    print("--- Quiz Bank Saved to quiz_bank.json ---")

if __name__ == "__main__":
    generate_and_save_quiz(10)
import fitz  # PyMuPDF
import ollama
import json

def ingest_pdf(file_path):
    """Extraction: Reads the PDF and returns the text."""
    print(f"--- Loading {file_path} ---")
    with fitz.open(file_path) as doc:
        text = " ".join([page.get_text() for page in doc])
    return text

def generate_quiz(text_context):
    """Generation: Creates questions based on the document."""
    print("--- Generating Quiz Questions ---")
    prompt = f"""
    Based on the text below, generate Multiple Choice Questions.
    Format your response exactly like this:
    Q1: [Question]
    A) [Option] B) [Option] C) [Option] D) [Option]
    Correct: [Letter]
    
    TEXT: {text_context[:3000]} # Using a slice to stay within model limits
    """
    system_instruction = (
        "You are a quiz creator. Return your response in VALID JSON only. "
        "The JSON must have these keys: 'question', 'options' (a list of 4 strings), "
        "and 'correct_answer' (the string content of the correct option)."
    )
    response = ollama.generate(model='gemma3:1b', system=system_instruction, prompt=prompt, format="json")
    quiz_data = json.loads(response['response'])
    return quiz_data

def evaluate_answer(question, user_answer, correct_answer):
    """Evaluation: Checks the user's input using the LLM for feedback."""
    print("--- Evaluating your Answer ---")
    prompt = f"""
    The question was: {question}
    The user answered: {user_answer}
    The correct answer is: {correct_answer}
    
    Briefly explain if the user is right or wrong and why in 2-3 sentences.
    """
    response = ollama.generate(model='gemma3:1b', prompt=prompt)
    return response['response']

if __name__ == "__main__":
    # 1. Ingestion
    content = ingest_pdf("Formula1_Overview.pdf")
    
    # 2. Question Generation
    quiz_output = generate_quiz(content)
    print("\n" + json.dumps(quiz_output, indent=2) + "\n")
    
    # 3. Simple Interaction (Manual Input)
    print("Question:", quiz_output['question'])
    print("Options:")
    for idx, option in enumerate(quiz_output['options']):
        print(f"{chr(65 + idx)}) {option}")
    user_input = input("Enter your answer for Q1 (e.g., A): ")
    
    # Note: In a real app, we would parse the 'Correct' letter from the LLM output.
    # For this simple version, let's just show how evaluation works.
    feedback = evaluate_answer(quiz_output['question'], user_input.upper(), quiz_output['correct_answer'])
    print("\nFeedback:\n", feedback)
    
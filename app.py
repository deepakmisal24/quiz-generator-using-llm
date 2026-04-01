import streamlit as st
import requests

st.set_page_config(page_title="F1 AI Academy", page_icon="🏎️", layout="wide")

# API Configuration
API_BASE = "http://localhost:8000"

# --- 1. Session State Initialization ---
if 'step' not in st.session_state:
    st.session_state.step = "UPLOAD" 
    st.session_state.quiz_data = []
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.feedback = None

# --- 2. Step: UPLOAD & PROCESS ---
if st.session_state.step == "UPLOAD":
    st.title("🏁 F1 AI Academy: Knowledge Ingester")
    st.markdown("Upload your technical PDF to generate a 2026-spec F1 quiz.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file and st.button("🚀 Process & Generate Quiz"):
        with st.spinner("Executing Pipeline: Extracting Text ➡️ Updating VectorDB ➡️ Generating AI Questions..."):
            # This triggers the api.py pipeline requested
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post(f"{API_BASE}/upload-and-process", files=files)
            
            if response.status_code == 200:
                # Fetch the generated quiz for the next steps
                st.session_state.quiz_data = requests.get(f"{API_BASE}/quiz-bank").json()
                st.session_state.step = "CHOICE"
                st.rerun()
            else:
                st.error("Pipeline Failed. Check API logs.")

# --- 3. Step: THE CHOICE ---
elif st.session_state.step == "CHOICE":
    st.title("🎯 Your AI Quiz is Ready!")
    st.write(f"I've generated {len(st.session_state.quiz_data)} questions based on your document.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔥 Take the Interactive Test", use_container_width=True):
            st.session_state.step = "TESTING"
            st.rerun()
    with col2:
        if st.button("📖 View All Questions & Answers", use_container_width=True):
            st.session_state.step = "VIEW_ALL"
            st.rerun()
    with col3:
        if st.button("🔍 Ask a Custom Question", use_container_width=True):
            st.session_state.step = "CUSTOM_QUERY"
            st.rerun()

# --- 4. Step Option 1: INTERACTIVE TESTING ---
elif st.session_state.step == "TESTING":
    q_idx = st.session_state.current_q
    item = st.session_state.quiz_data[q_idx]
    
    st.progress((q_idx + 1) / len(st.session_state.quiz_data))
    st.subheader(f"Question {q_idx + 1} of {len(st.session_state.quiz_data)}")
    st.info(item['question'])
    
    # Logic to handle answering
    if not st.session_state.feedback:
        choice = st.radio("Choose your answer:", item['options'], index=None)
        if st.button("Submit Answer") and choice:
            user_letter = chr(65 + item['options'].index(choice))
            
            # API Evaluation call
            res = requests.post(f"{API_BASE}/evaluate", json={
                "question": item['question'],
                "user_answer": user_letter,
                "correct_answer": item['correct_answer'],
                "context_used": item['context_used']
            }).json()
            
            st.session_state.feedback = res
            if res['verdict'] == "CORRECT":
                st.session_state.score += 1
            st.rerun()
    else:
        # Display Result and Explanation
        res = st.session_state.feedback
        if res['verdict'] == "CORRECT":
            st.success(f"✅ Correct! (Current Score: {st.session_state.score})")
        else:
            st.error(f"❌ Incorrect. The right answer was {item['correct_answer']}")
        
        st.write(f"**Expert Explanation:** {res['explanation']}")
        
        if st.button("Next Question ➡️"):
            if st.session_state.current_q + 1 < len(st.session_state.quiz_data):
                st.session_state.current_q += 1
                st.session_state.feedback = None
                st.rerun()
            else:
                st.session_state.step = "RESULTS"
                st.rerun()
        

# --- 4. Step Option 2: VIEW ALL CONTENT ---
elif st.session_state.step == "VIEW_ALL":
    st.title("📚 Study Guide: All Generated Content")
    st.write("Review all questions generated from your technical documents.")
    
    for i, item in enumerate(st.session_state.quiz_data):
        with st.expander(f"Question {i+1}: {item['question']}"):
            for idx, opt in enumerate(item['options']):
                label = chr(65+idx)
                if label == item['correct_answer']:
                    st.write(f"✅ **{label}) {opt}**")
                else:
                    st.write(f"{label}) {opt}")
    
    if st.button("🔙 Back to Choice"):
        st.session_state.step = "CHOICE"
        st.rerun()
    elif st.button("🔄 Start New Upload"):
        # Reset everything
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 4. Step Option 3: CUSTOM QUERY MODE ---
elif st.session_state.step == "CUSTOM_QUERY":
    st.title("🔍 Technical Query Assistant")
    st.write("Ask any specific question about the uploaded document.")
    
    user_query = st.text_input("Enter your question (e.g., 'What is the F1?')")
    
    if st.button("Get Answer"):
        if user_query:
            with st.spinner("Searching the PDF..."):
                res = requests.post(f"{API_BASE}/ask-custom", json={"query": user_query}).json()
                st.markdown("### 🤖 AI Response:")
                st.info(res['answer'])
        else:
            st.warning("Please enter a question first.")
            
    if st.button("🔙 Back to Choice"):
        st.session_state.step = "CHOICE"
        st.rerun()
    elif st.button("🔄 Start New Upload"):
        # Reset everything
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 5. Final Results Screen ---
elif st.session_state.step == "RESULTS":
    st.balloons()
    st.title("🏆 Quiz Complete!")
    st.metric("Final Score", f"{st.session_state.score} / {len(st.session_state.quiz_data)}")
    
    if st.button("🔄 Start New Upload"):
        # Reset everything
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    elif st.button("🔙 Back to Choice"):
            st.session_state.step = "CHOICE"
            st.rerun()
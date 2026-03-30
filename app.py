import streamlit as st
import requests

st.set_page_config(page_title="F1 Turbo Quiz", page_icon="🏎️")
st.title("🏎️ F1: The 2026 Era Quiz")

API_BASE = "http://localhost:8000"

# 1. Initialize Session State
if 'questions' not in st.session_state:
    try:
        res = requests.get(f"{API_BASE}/quiz-data")
        st.session_state.questions = res.json()
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.quiz_over = False
        st.session_state.answered = False  # Track if current Q is answered
        st.session_state.feedback = None   # Store API response
    except:
        st.error("Cannot connect to API. Run 'uvicorn api:app' first.")
        st.stop()

# 2. Quiz Logic
if not st.session_state.quiz_over:
    q_idx = st.session_state.current_q
    q_item = st.session_state.questions[q_idx]
    
    st.write(f"### Question {q_idx + 1} of {len(st.session_state.questions)}")
    st.info(q_item['question'])
    
    # 3. Answering Phase
    if not st.session_state.answered:
        choice = st.radio("Options:", q_item['options'], index=None)
        
        if st.button("Submit Answer"):
            if choice:
                user_letter = chr(65 + q_item['options'].index(choice))
                
                # Call API
                res = requests.post(f"{API_BASE}/verify", json={
                    "question": q_item['question'],
                    "user_answer": user_letter,
                    "correct_answer": q_item['correct_answer'],
                    "context_used": q_item['context_used']
                }).json()
                
                # Update State
                st.session_state.feedback = res
                st.session_state.answered = True
                if res['verdict'] == "CORRECT":
                    st.session_state.score += 1
                st.rerun()
            else:
                st.warning("Please select an option first.")

    # 4. Feedback Phase (Shows after clicking Submit)
    else:
        res = st.session_state.feedback
        if res['verdict'] == "CORRECT":
            st.success(f"✅ Correct! (Score: {st.session_state.score})")
        else:
            st.error(f"❌ Wrong. The correct answer was {q_item['correct_answer']}")
        
        st.write(f"**Explanation:** {res['explanation']}")
        
        if st.button("Next Question ➡️"):
            # Increment Index
            if st.session_state.current_q + 1 < len(st.session_state.questions):
                st.session_state.current_q += 1
                st.session_state.answered = False
                st.session_state.feedback = None
            else:
                st.session_state.quiz_over = True
            st.rerun()

# 5. Final Screen
else:
    st.balloons()
    st.header("🏆 Quiz Finished!")
    # F1 Points are usually 25 for a win
    st.metric("Total Correct", f"{st.session_state.score} / {len(st.session_state.questions)}")
    
    if st.button("Restart Quiz"):
        # Clear specific keys to restart
        for key in ['questions', 'current_q', 'score', 'quiz_over', 'answered', 'feedback']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
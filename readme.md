


# Problem Statement: Quiz Application with Document-Based Question Generation and LLM Evaluation

An automated, AI-driven pipeline designed to transform complex documents into interactive, grounded learning experiences. This project leverages **Retrieval-Augmented Generation (RAG)** to ensure that every quiz question and explanation is strictly derived from specific technical sources, such as the 2026 Power Unit regulations.

---

## DEMO

[Project Demo link](https://youtu.be/uePcjf5rI2c)

---

## 🚀 The Vision
The application provides a seamless "Upload-to-Learn" workflow:
1.  **Ingest**: Upload a technical PDF (e.g., FIA 2026 Regulations).
2.  **Process**: The system extracts text, chunks it, and stores it in a **ChromaDB** vector database.
3.  **Generate**: **Ollama (Qwen2.5 and Deepseek-r1)** analyzes the data to create unique multiple-choice questions.
4.  **Engage**: Users choose between an **Interactive Test** with real-time AI feedback or a **Study Guide** view.

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit (State-managed UI)
- **Backend**: FastAPI (Asynchronous Orchestration)
- **LLM**: Ollama (`qwen2.5:3b` and `deepseek-r1:1.5b`)
- **Vector Database**: ChromaDB
- **PDF Processing**: PyMuPDF (fitz)

---

## 📂 Project Architecture
- `app.py`: The UI engine. Manages navigation and session state.
- `api.py`: The orchestrator. Connects the frontend to the processing modules.
- `indigest_pdf.py`: PDF text extraction and chunking logic.
- `vector_engine.py`: ChromaDB manager for embeddings and database resets.
- `generate_quiz.py`: RAG-based MCQ generation.
- `main.py`: Logic for evaluation and custom user queries.

---

## ⚙️ Setup & Installation

### 1. Prerequisites
Ensure **Ollama** is running and the model is pulled:
```bash
ollama pull qwen2.5:3b deepseek-r1:1.5b
```

### 2. Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Execution
#### Terminal A (API):
```bash
uvicorn api:app --reload
```

#### Terminal B (UI):
```bash
streamlit run app.py
```

---


# 🩺 Heart Disease RAG Assistant

A high-performance, precision-guided Retrieval-Augmented Generation (RAG) assistant designed to analyze heart disease patient data with 100% numeric accuracy. Built with a "Heuristic-First" architecture to eliminate LLM hallucinations for specific patient lookups.

![App Screenshot](frontend/src/assets/hero.png)

## 🚀 Key Features
- **Hybrid Retrieval Engine**: Combines exact numeric matching (Age, Sex, Cholesterol) with semantic vector search (ChromaDB).
- **Healthcare Guardrails**: Robust regex-based filtering to block off-topic queries and medical advice, ensuring strict dataset focus.
- **Diagnostic Transparency**: Real-time feedback on "Exact Matches" vs "Similar Cases" to build user trust.
- **Cinema-Grade UI**: A premium, responsive React interface with interactive data visualization.
- **Cloud Ready**: Fully Dockerized and optimized for one-click deployment to **Railway**.

## 🛠️ Technology Stack
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React + Vite + TypeScript
- **LLM**: Groq (Llama-3.1-8b-instant)
- **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
- **Vector Store**: ChromaDB
- **Data**: Pandas (Analyzing 918 patients from the UCI Heart Disease dataset)

## 💻 Local Setup

### 1. Prerequisite: API Key
You need a [Groq API Key](https://console.groq.com/keys).

### 2. Launch the Application
The simplest way to run both the API and the UI locally:
```bash
./launch_app.bat
```
This script will:
1. Clean up stale database locks.
2. Initialize the backend on port `8000`.
3. Start the Vite dev server on port `5173`.
4. Automatically open your browser.

## ☁️ Deployment (Railway)
This repository is pre-configured for **Railway** as a single unified service.

1. Create a **New Project** on Railway from this GitHub repo.
2. Add the following Environment Variable in the Railway dashboard:
   - `GROQ_API_KEY`: your-api-key-here
3. The `Dockerfile` at the root handles the multi-stage build (Node.js build followed by Python serving).

## 📊 Dataset Attribution
The data used in this project is based on the **UCI Heart Disease Dataset**, featuring 11 clinical features used to predict heart disease.

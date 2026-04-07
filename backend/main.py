from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
import os
import subprocess
import pandas as pd
import re
import time

app = FastAPI()

# In production, we explicitly allow the Railway domain and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths for container environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "backend", "chroma_db")
DATASET_PATH = os.path.join(BASE_DIR, "heart_dataset.csv")
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
vectorstore = None
all_patient_texts = []
all_patient_meta = []
dataset_summary = ""

def initialize_system():
    global vectorstore, all_patient_texts, all_patient_meta, dataset_summary
    
    # 1. Clean locks
    if os.path.exists(CHROMA_PATH):
        for lock_file in ["chroma.sqlite3-journal", "chroma.sqlite3-shm", "chroma.sqlite3-wal"]:
            path = os.path.join(CHROMA_PATH, lock_file)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

    # 2. Auto-ingest if DB missing
    if not os.path.exists(CHROMA_PATH):
        print(f"Vector DB missing at {CHROMA_PATH}. Ingesting {DATASET_PATH}...")
        try:
            # Run ingest.py from within the backend directory context
            subprocess.run(["python", os.path.join(BASE_DIR, "backend", "ingest.py")], check=True)
        except Exception as e:
            print(f"Ingestion failed: {e}")

    # 3. Load Vectorstore
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings, collection_name="heart_disease")
    except Exception as e:
        print(f"Vectorstore init failed: {e}")

    # 4. Sync Raw Data for Hensics
    if os.path.exists(DATASET_PATH):
        df = pd.read_csv(DATASET_PATH)
        for idx, row in df.iterrows():
            hd_str = "Yes" if row['HeartDisease'] == 1 else "No"
            text = (
                f"PATIENT_RECORD: Age is {row['Age']}, Sex is {row['Sex']}, "
                f"Cholesterol is {row['Cholesterol']}, Heart Disease: {hd_str}. "
                f"(Details: ChestPain={row['ChestPainType']}, BP={row['RestingBP']}, BS={row['FastingBS']}, ECG={row['RestingECG']}, MaxHR={row['MaxHR']})"
            )
            all_patient_texts.append(text)
            all_patient_meta.append(row.to_dict())

        total = len(df)
        hd_count = int(df["HeartDisease"].sum())
        dataset_summary = (
            f"Total Patients: {total}. WITH disease: {hd_count}. WITHOUT disease: {total-hd_count}. "
            f"Oldest: {df['Age'].max()}. Max Cholesterol: {df['Cholesterol'].max()}."
        )

        # Free memory aggressively to stay under free tier limits
        import gc
        del df
        gc.collect()

# Initialize on startup
initialize_system()

# LLM Config (Railway Env Var)
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0, groq_api_key=GROQ_KEY)

NOISE_NUMBERS = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}
AGGREGATE_KEYWORDS = re.compile(r'\b(how many|count|total|average|mean|distribution|stats|statistics|summary)\b', re.IGNORECASE)
OUT_OF_DOMAIN = re.compile(r'\b(medication|drug|pill|capital|country|recipe|politics|history)\b', re.IGNORECASE)

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "db": vectorstore is not None, "records": len(all_patient_texts)}

@app.post("/query")
async def query_endpoint(req: QueryRequest):
    query = req.query
    if OUT_OF_DOMAIN.search(query):
        return {"answer": "Guardrail: I only answer questions about the heart disease dataset.", "metadata": []}

    is_aggregate = bool(AGGREGATE_KEYWORDS.search(query))
    nums = set(re.findall(r'\b\d+\b', query)) - NOISE_NUMBERS
    sex = 'F' if re.search(r'\b(female|woman|lady|her)\b', query, re.IGNORECASE) else ('M' if re.search(r'\b(male|man|guy|his)\b', query, re.IGNORECASE) else None)

    heuristic_results = []
    if nums:
        for idx, text in enumerate(all_patient_texts):
            text_nums = set(re.findall(r'\b\d+\b', text))
            if nums.issubset(text_nums):
                if sex and all_patient_meta[idx].get('Sex') != sex: continue
                heuristic_results.append(text)

    semantic_results = []
    if vectorstore:
        try:
            docs = vectorstore.similarity_search_with_score(query, k=5)
            semantic_results = [doc.page_content for doc, score in docs if score < 0.6]
        except: pass

    full_context = []
    if heuristic_results:
        full_context.extend([f"[EXACT MATCH] {r}" for r in heuristic_results[:10]])
    if semantic_results:
        for r in semantic_results:
            if not any(r in h for h in heuristic_results):
                full_context.append(f"[SIMILAR CASE] {r}")

    context_str = "\n".join(full_context[:10]) if full_context else "(No relevant cases found)"
    stats_str = f"\n\nDATASET STATISTICS:\n{dataset_summary}" if is_aggregate else ""

    prompt = f"Records:\n{context_str}{stats_str}\n\nQuestion: {query}\nAnswer accurately and concisely:"

    try:
        ans = llm.invoke(prompt).content
    except Exception as e:
        ans = f"LLM Error: {e}"

    return {"answer": ans, "metadata": []}

# ── Serve Frontend ───────────────────────────────────────────────────────────
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

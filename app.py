import streamlit as st
import os
import re
import pandas as pd
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

# Setup layout
st.set_page_config(page_title="HITECH Heart Disease RAG", layout="wide", page_icon="🫀")

# Custom cinematic dark styling inspired by HITECH
st.markdown("""
<style>
    body {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    .stChatFloatingInputContainer {
        border-top: 1px solid #1E2530;
    }
    h1 {
        color: #4DB8FF;
        font-family: inherit;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🫀 Heart Disease Clinical Assistant")
st.caption("Secure AI Assistant powered by internal dataset. Authorized personnel only.")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "backend", "chroma_db")
DATASET_PATH = os.path.join(BASE_DIR, "heart_dataset.csv")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# System Initialization logic cached
@st.cache_resource(show_spinner=False)
def load_system():
    vectorstore = None
    all_patient_texts = []
    all_patient_meta = []
    dataset_summary = ""
    
    # 3. Load Vectorstore
    if os.path.exists(CHROMA_PATH):
        try:
            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings, collection_name="heart_disease")
        except Exception as e:
            st.error(f"Vectorstore init failed: {e}")
    else:
        st.warning(f"Vector DB missing at {CHROMA_PATH}. Please run the ingest.py script beforehand.")

    # 4. Sync Raw Data for Heuristics
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

        import gc
        del df
        gc.collect()
        
    return vectorstore, all_patient_texts, all_patient_meta, dataset_summary

with st.spinner("Initializing Clinical Search Terminal..."):
    vectorstore, all_patient_texts, all_patient_meta, dataset_summary = load_system()

# LLM setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

if not GROQ_API_KEY:
    st.error("Please set GROQ_API_KEY environment variable or in Streamlit secrets.")
    st.stop()

# Regex setups
NOISE_NUMBERS = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}
AGGREGATE_KEYWORDS = re.compile(r'\b(how many|count|total|average|mean|distribution|stats|statistics|summary)\b', re.IGNORECASE)
OUT_OF_DOMAIN = re.compile(r'\b(medication|drug|pill|capital|country|recipe|politics|history)\b', re.IGNORECASE)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

query = st.chat_input("Enter clinical query...")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
        
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if OUT_OF_DOMAIN.search(query):
            ans = "Guardrail: I only answer questions about the heart disease dataset."
            message_placeholder.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        else:
            with st.spinner("Accessing patient database..."):
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
                    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0, groq_api_key=GROQ_API_KEY)
                    ans = llm.invoke(prompt).content
                except Exception as e:
                    ans = f"LLM Error: {e}"
                
                message_placeholder.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                
                # Expandable diagnostics for transparency
                with st.expander("Diagnostics context"):
                    st.write(f"Aggregate mode: {is_aggregate}")
                    st.write(f"Heuristics size: {len(heuristic_results)}")
                    st.write(f"Semantic size: {len(semantic_results)}")

import pandas as pd
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
import os

CSV_PATH = "../heart_dataset.csv"
CHROMA_PATH = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def ingest():
    print(f"Loading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    docs = []
    
    # Process each row
    for index, row in df.iterrows():
        # Build semantic representation
        text_content = (
            f"Patient Context: Age is {row['Age']}, Sex is {row['Sex']}, "
            f"Chest Pain Type is {row['ChestPainType']}, Resting Blood Pressure is {row['RestingBP']}, "
            f"Cholesterol is {row['Cholesterol']}, Fasting Blood Sugar is {row['FastingBS']}, "
            f"Resting ECG is {row['RestingECG']}, Maximum Heart Rate is {row['MaxHR']}, "
            f"Exercise Induced Angina is {row['ExerciseAngina']}, Oldpeak is {row['Oldpeak']}, "
            f"ST Slope is {row['ST_Slope']}, Heart Disease status is {row['HeartDisease']}."
        )
        
        # Keep raw features as metadata for the frontend 3D cards
        metadata = row.to_dict()
        # Ensure primitive types for chromadb metadata
        metadata = {k: (float(v) if isinstance(v, (int, float)) else str(v)) for k, v in metadata.items()}
        metadata["row_id"] = index
        
        docs.append(Document(page_content=text_content, metadata=metadata))
    
    print(f"Loaded {len(docs)} documents. Initializing embeddings...")
    hf_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    import shutil
    if os.path.exists(CHROMA_PATH):
        print("Existing DB found, deleting it to avoid schema mismatch.")
        shutil.rmtree(CHROMA_PATH)

    print(f"Persisting vectors to {CHROMA_PATH}...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=hf_embeddings,
        persist_directory=CHROMA_PATH,
        collection_name="heart_disease",
        collection_metadata={"hnsw:space": "cosine"}
    )
    
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest()

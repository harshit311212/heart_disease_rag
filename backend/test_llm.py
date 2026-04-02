import os
from langchain_groq import ChatGroq

context_texts = [
    "Patient Context: Age is 40, Sex is M, Chest Pain Type is ATA, Resting Blood Pressure is 140, Cholesterol is 289, Fasting Blood Sugar is 0, Resting ECG is Normal, Maximum Heart Rate is 172, Exercise Induced Angina is N, Oldpeak is 0.0, ST Slope is Up, Heart Disease status is 0."
]
query = "Tell me about the 40-year old male patient who has a cholesterol level of 289. Does he have heart disease?"
prompt = f"""Use the following snippets of tabular data context about patients to answer the user's question. 
If you don't know the answer or the context doesn't have it, just say you don't know. DO NOT hallucinate.

Context:
{" | ".join(context_texts)}

Question: {query}

Answer perfectly and concisely:"""

# os.environ["GROQ_API_KEY"] = "YOUR_KEY_HERE"
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
response = llm.invoke(prompt)
print(response.content)

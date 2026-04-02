import os
from PyPDF2 import PdfReader

files = ['heart_PRD.pdf', 'heart_Tech_Stack.pdf', 'heart_Design_Doc.pdf']
cwd = 'd:/Sample projs/Heart_Disease_RAG'

for f in files:
    path = os.path.join(cwd, f)
    print(f"--- {f} ---")
    try:
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):
            print(f"Page {i+1}:")
            print(page.extract_text())
    except Exception as e:
        print(f"Error reading {f}: {e}")
    print("\n\n")

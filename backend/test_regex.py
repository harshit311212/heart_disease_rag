import re
import pandas as pd
raw_df = pd.read_csv('../heart_dataset.csv')
all_patient_texts = []
for index, row in raw_df.iterrows():
    text_content = f"Patient Context: Age is {row['Age']}, Sex is {row['Sex']}, Chest Pain Type is {row['ChestPainType']}, Resting Blood Pressure is {row['RestingBP']}, Cholesterol is {row['Cholesterol']}, Fasting Blood Sugar is {row['FastingBS']}, Resting ECG is {row['RestingECG']}, Maximum Heart Rate is {row['MaxHR']}, Exercise Induced Angina is {row['ExerciseAngina']}, Oldpeak is {row['Oldpeak']}, ST Slope is {row['ST_Slope']}, Heart Disease status is {row['HeartDisease']}."
    all_patient_texts.append(text_content)

query = "Tell me about the 40-year old male patient who has a cholesterol level of 289. Does he have heart disease?"
numbers = set(re.findall(r'\d+', query))
context_texts = []
if numbers:
    print("Numbers found in query:", numbers)
    for idx, text in enumerate(all_patient_texts):
        if all(re.search(fr'\b{num}\b', text) for num in numbers):
            print("MATCHED PATIENT:", text)
            context_texts.append(text)

if not context_texts:
    print("NO PATIENTS MATCHED!")

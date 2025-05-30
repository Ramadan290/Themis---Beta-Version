import os
import pandas as pd
import numpy as np
import joblib
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, MinMaxScaler


# Define paths
ML_DIR = os.path.dirname(os.path.abspath(__file__))  
BCR_MODEL_PATH = os.path.join(ML_DIR, "bcr_model.pkl")
BCR_ENCODER_PATH = os.path.join(ML_DIR, "bcr_encoder.pkl")
BCR_SCALER_PATH = os.path.join(ML_DIR, "bcr_scaler.pkl")
BCR_FEATURES_PATH = os.path.join(ML_DIR, "bcr_features.pkl")  

# API request headers with authentication
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBbG95Iiwicm9sZSI6ImhyIiwiZXhwIjoxNzM4NTc5ODE3fQ.TgRYLRvwYHJC-15M9saomWqaHsDls6prJcdj_iatssU"  # Replace with real token
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# Fetch employee data with authentication
url = "http://127.0.0.1:8000/classification/bcr_data/all"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()["employees_data"]
    print("✅ Successfully fetched data!")
else:
    print(f"❌ Error fetching data: {response.status_code}")
    print(response.text)  # Debugging
    exit()

# Convert to DataFrame
df = pd.DataFrame(data)

# 🔹 Define expected numerical and categorical columns
numerical_cols = [
    "salary", "total_appraisals", "total_penalties", "total_raise_requests", 
    "completion_rate" , "project_contribtution"  
]
categorical_cols = ["workload_handling"]

# 🔹 Handle missing numerical values (set to 0)
for col in numerical_cols:
    if col not in df.columns:
        df[col] = 0  
df[numerical_cols] = df[numerical_cols].fillna(0) 

# 🔹 Ensure `workload_handling` is always present
if "workload_handling" not in df.columns:
    df["workload_handling"] = "Unknown"  
df["workload_handling"] = df["workload_handling"].fillna("Unknown")

# 🔹 Encode categorical values **before defining feature names**
encoder = LabelEncoder()
df["workload_handling"] = encoder.fit_transform(df["workload_handling"])

# 🔹 Normalize numerical values (Ensure feature names are preserved)
scaler = MinMaxScaler()
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

feature_names = numerical_cols + ["workload_handling"]
joblib.dump(feature_names, BCR_FEATURES_PATH) 
joblib.dump(encoder, BCR_ENCODER_PATH)  
joblib.dump(scaler, BCR_SCALER_PATH) 

# 🔹 Generate target variable
df["bcr"] = (df["salary"] + df["total_appraisals"]) / \
            (df["total_penalties"] + df["total_raise_requests"] + 1) * \
            (df["project_contribtution"] + 1) * (df["completion_rate"] + 1 ) 

y = df["bcr"]
X = df[feature_names] 
# 🔹 Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 Train RandomForest model
model = RandomForestRegressor(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

# 🔹 Saving model and preprocessing tools
joblib.dump(model, BCR_MODEL_PATH)

print("\n📌 Features Used in Training:")
for idx, feature in enumerate(feature_names):
    print(f"{idx + 1}. {feature}")

print("✅ LabelEncoder Categories for workload_handling:")
print(list(encoder.classes_))

print("✅ BCR Model Trained and Saved Successfully!")
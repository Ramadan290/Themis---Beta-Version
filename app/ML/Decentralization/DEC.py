# Model with Randomized Controlled Overrides (This is a BETA version)

import os
import pandas as pd
import numpy as np
import joblib
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler

# ✅ Define Paths
ML_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(ML_DIR, "dec_model.pkl")
SCALER_PATH = os.path.join(ML_DIR, "dec_scaler.pkl")
FEATURES_PATH = os.path.join(ML_DIR, "dec_features.pkl")

# ✅ API Authentication
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBbG95Iiwicm9sZSI6ImhyIiwiZXhwIjoxNzM4NjExMDIxfQ.pM_OL7_8nIRiyPjiN0FL6Knpq8XOdYAHWSn8TRAblwI"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# ✅ Fetch Employee Data
url = "http://127.0.0.1:8000/classification/decentralization_data/all"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()["employees_data"]
    print("✅ Successfully fetched employee data!")
else:
    print(f"❌ Error fetching data: {response.status_code}")
    print(response.text)  # Debugging
    exit()

# ✅ Convert to DataFrame
df = pd.DataFrame(data)

# ✅ Map workload handling to numerical values
workload_mapping = {"Light": 0, "Balanced": 1, "High": 2}
df["workload_handling"] = df["workload_handling"].map(workload_mapping).fillna(1)  # Default to "Balanced"

# ✅ Extract Number of Completed Projects
df["completed_projects"] = df["project_contribtution"].apply(lambda x: sum(1 for p in x if p["status"] == "Completed"))

# ✅ One-Hot Encode Skills
skills_set = set(skill for skills in df["skills"] for skill in skills)
for skill in skills_set:
    df[skill] = df["skills"].apply(lambda x: 1 if skill in x else 0)
df.drop(columns=["skills"], inplace=True)

# ✅ Normalize Numerical Values
numerical_cols = ["completion_rate", "experience_years", "completed_projects"]
scaler = MinMaxScaler()
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

# ✅ Handle Missing Departments — Predict Most Suitable Department
if df["department"].isnull().any():
    print("⚠️ Some employees have no department assigned. Proceeding to predict the best fit...")
    
    # Fetch all available departments
    dept_response = requests.get("http://127.0.0.1:8000/departments/all", headers=headers)
    if dept_response.status_code == 200:
        departments = [dept["department"] for dept in dept_response.json().get("departments", [])]
        print("✅ Departments fetched for prediction:", departments)
    else:
        print(f"❌ Error fetching departments: {dept_response.status_code}")
        exit()
else:
    print("✅ All employees have assigned departments.")

# ✅ Prepare Feature and Target Columns
feature_names = numerical_cols + ["workload_handling"] + list(skills_set)
X = df[feature_names]
y = df["department"]

# ✅ Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Train Classification Model
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

# ✅ Save Model & Preprocessing Tools
joblib.dump(model, MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)
joblib.dump(feature_names, FEATURES_PATH)

# ✅ Debugging Output
print("\n📌 Features Used in Training:")
for idx, feature in enumerate(feature_names):
    print(f"{idx + 1}. {feature}")

print("\n✅ Employee Decentralization Model Trained and Saved Successfully!")

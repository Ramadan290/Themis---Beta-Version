import os
import pandas as pd
import numpy as np
import joblib
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler

# Define paths
WB_DIR = os.path.dirname(os.path.abspath(__file__))  
WB_MODEL_PATH = os.path.join(WB_DIR, "WB_model.pkl")
WB_SCALER_PATH = os.path.join(WB_DIR, "WB_scaler.pkl")
WB_FEATURES_PATH = os.path.join(WB_DIR, "WB_features.pkl")

# 🔹 Use the HR token you obtained earlier
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBbG95Iiwicm9sZSI6ImhyIiwiZXhwIjoxNzM4NjA5MDU2fQ.tGyrDUJREYZaHvd9WMQ8RS80bDxplujLFvpqtefDUiw"  # Replace with real token

# API request headers with authentication
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# Fetch employee data with authentication
url = "http://127.0.0.1:8000/classification/well_being/employee_data/all"
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

# 🔹 Ensure `interaction_level` exists and is correctly formatted
interaction_cols = ["messages_sent", "meetings_attended", "conflicts_involved"]
for col in interaction_cols:
    df[col] = df["interaction_level"].apply(lambda x: x.get(col, 0) if isinstance(x, dict) else 0)

# Drop the original nested dictionary column
df.drop(columns=["interaction_level"], inplace=True, errors="ignore")

# 🔹 Convert `workload_handling` to numerical values
workload_mapping = {"Low": 0, "Balanced": 1, "High": 2}
df["workload_handling"] = df["workload_handling"].map(workload_mapping).fillna(1)  # Default to "Balanced"

# 🔹 Select only valid numerical features for the model
numerical_cols = [
    "completion_rate", "project_contribtution", "total_present_days", 
    "total_absent_days", "total_late_days", "total_on_leave_days", "salary", 
    "total_appraisals", "total_penalties", "total_benefits", "total_raise_requests",
    "messages_sent", "meetings_attended", "conflicts_involved", "workload_handling"  # ✅ Now numerical
]
df[numerical_cols] = df[numerical_cols].fillna(0)

# 🔹 Normalize numerical values
scaler = MinMaxScaler()
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

# 🔹 Save the list of correct features
feature_names = numerical_cols
joblib.dump(feature_names, WB_FEATURES_PATH)

# 🔹 Generate random labels for now
df["wellbeing_category"] = np.random.choice(["Good", "Neutral", "At Risk"], len(df))
y = df["wellbeing_category"].astype("category").cat.codes
X = df[feature_names]

# 🔹 Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 Train RandomForest model
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

# 🔹 Save model and preprocessing tools
joblib.dump(model, WB_MODEL_PATH)
joblib.dump(scaler, WB_SCALER_PATH)

print("✅ AI Model Trained and Saved Successfully!")
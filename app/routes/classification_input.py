from fastapi import APIRouter, HTTPException, Depends , Form
from app.auth import get_current_user
from app.models import User , DepartmentUpdateRequest
from app.config import (
    users_collection, payroll_collection, attendance_collection, status_collection , skills_collection ,departments_collection
)
import pandas as pd
import joblib
import requests
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import os
import time
import numpy as np
from pydantic import BaseModel
import random




router = APIRouter()








################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
                                    #Employee Well being Model
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################


################################################################################################################
# 📌 Load Machine Learning Model & Preprocessing Tools
################################################################################################################

# Define paths for ML models
WB_DIR = os.path.join(os.path.dirname(__file__), "..", "ML","Well_Being")
WB_MODEL_PATH = os.path.join(WB_DIR, "WB_model.pkl")
WB_ENCODER_PATH = os.path.join(WB_DIR, "WB_encoder.pkl")
WB_SCALER_PATH = os.path.join(WB_DIR, "WB_scaler.pkl")
WB_FEATURES_PATH = os.path.join(WB_DIR, "WB_features.pkl") 
WB_WORKLOAD_ENCODER_PATH = os.path.join(WB_DIR,"WB_workload_encoder.pkl")




start_time = time.time()

# Load model, encoder, and scaler
try:
    print("Loading AI model...")
    model = joblib.load(WB_MODEL_PATH)
    encoder = joblib.load(WB_ENCODER_PATH)
    scaler = joblib.load(WB_SCALER_PATH)
    features = joblib.load(WB_FEATURES_PATH)
    print(f"✅ Model loaded in {time.time() - start_time:.2f} seconds!")

except FileNotFoundError as e:
    model, encoder, scaler = None, None, None
    print(f"❌ AI model or preprocessing files not found: {e}")

################################################################################################################
# 📌 Fetch Data for a Specific Employee
################################################################################################################

@router.get("/well_being/{username}")
async def get_employee_data(username: str, current_user: dict = Depends(get_current_user)):
    # Ensure only HR users can access AI data
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Unauthorized: Only HR can access AI data.")

    try:
        # Fetch data from multiple collections
        user = users_collection.find_one({"username": username}, {"_id": 0})
        payroll = payroll_collection.find_one({"username": username}, {"_id": 0})
        attendance_records = list(attendance_collection.find({"username": username}, {"_id": 0}))
        status = status_collection.find_one({"username": username}, {"_id": 0}) if user else None

        # Validate if all necessary data exists
        if not (user and payroll and attendance_records and status):
            raise HTTPException(status_code=404, detail="Employee data missing from one or more collections.")

        # Summarize payroll data
        total_salary = payroll.get("salary", 0)
        total_appraisals = sum(appraisal.get("amount", 0) for appraisal in payroll.get("appraisals", []))
        total_penalties = sum(penalty.get("amount", 0) for penalty in payroll.get("penalties", []))
        total_benefits = len(payroll.get("benefits", []))
        total_raise_requests = len(payroll.get("raise_requests", []))

        # Summarize attendance data
        total_present = sum(1 for record in attendance_records if record.get("status") == "Present")
        total_absent = sum(1 for record in attendance_records if record.get("status") == "Absent")
        total_late = sum(1 for record in attendance_records if record.get("status") == "Late")



        # Summarize project contributions (Fixed typo in "project_contribtution")
        project_contribution_count = len(status.get("project_contribtution", []))

        # Structure the summarized data
        employee_data = {
            "username": user.get("username", ""),
            "completion_rate": status.get("completion_rate", 0),
            "project_contribtution": project_contribution_count,
            "interaction_level": status.get("interaction_level", {}),
            "workload_handling": status.get("workload_handling", ""),
            "total_present_days": total_present,
            "total_absent_days": total_absent,
            "total_late_days": total_late,
            "salary": total_salary,
            "total_appraisals": total_appraisals,
            "total_penalties": total_penalties,
            "total_benefits": total_benefits,
            "total_raise_requests": total_raise_requests
        }

        return {"status": "success", "employee_data": employee_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


################################################################################################################
# 📌 Fetch Data for All Employees
################################################################################################################

@router.get("/well_being/employee_data/all")
async def get_all_employees_data(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Unauthorized: Only HR can access AI data.")

    try:
        print("🔍 Fetching all payroll, status, and attendance data...")

        # Fetch all payroll, status, and attendance data at once
        payrolls = list(payroll_collection.find({}, {
            "_id": 0, "username": 1, "salary": 1, "appraisals": 1, "penalties": 1,
            "raise_requests": 1, "benefits": 1
        }))
        statuses = list(status_collection.find({}, {
            "_id": 0, "username": 1, "completion_rate": 1, "project_contribtution": 1,
            "workload_handling": 1, "interaction_level": 1
        }))
        attendance_records = list(attendance_collection.find({}, {
            "_id": 0, "username": 1, "status": 1
        }))

        # Convert lists to dictionaries for quick lookups
        payroll_dict = {p["username"]: p for p in payrolls}
        status_dict = {s["username"]: s for s in statuses}
        attendance_dict = {}

        # ✅ Fix: Ensure all attendance statuses are initialized correctly
        for record in attendance_records:
            username = record["username"]
            if username not in attendance_dict:
                attendance_dict[username] = {"Present": 0, "Absent": 0, "Late": 0, "On Leave": 0}  # Include 'On Leave'
            
            attendance_status = record["status"]
            if attendance_status not in attendance_dict[username]:  
                attendance_dict[username][attendance_status] = 0  # Ensure any new status is initialized
            
            attendance_dict[username][attendance_status] += 1

        # Prepare the final data list
        all_employees_data = []

        # ✅ Fix: Process only employees with payroll data
        for payroll in payrolls:
            username = payroll["username"]
            status = status_dict.get(username, {})
            attendance = attendance_dict.get(username, {"Present": 0, "Absent": 0, "Late": 0, "On Leave": 0})

            # ✅ Fix: Ensure `project_contribtution` is always a list
            project_contributions = status.get("project_contribtution", [])
            completed_projects = sum(1 for project in project_contributions if isinstance(project, dict) and project.get("status") == "Completed")

            # ✅ Fix: Ensure `interaction_level` has a consistent structure
            interaction_level = status.get("interaction_level", {})
            interaction_level = {
                "messages_sent": interaction_level.get("messages_sent", 0),
                "meetings_attended": interaction_level.get("meetings_attended", 0),
                "conflicts_involved": interaction_level.get("conflicts_involved", 0),
            }

            # ✅ Fix: Default `workload_handling` to "balanced" instead of "unknown"
            workload_handling = status.get("workload_handling", "balanced")

            # Structure final employee data
            employee_data = {
                "username": username,
                "completion_rate": status.get("completion_rate", 0),
                "project_contribtution": completed_projects,  # Keeping typo
                "interaction_level": interaction_level,
                "workload_handling": workload_handling,
                "total_present_days": attendance["Present"],
                "total_absent_days": attendance["Absent"],
                "total_late_days": attendance["Late"],
                "total_on_leave_days": attendance["On Leave"],
                "salary": payroll.get("salary", 0),
                "total_appraisals": sum(a.get("amount", 0) for a in payroll.get("appraisals", [])),
                "total_penalties": sum(p.get("amount", 0) for p in payroll.get("penalties", [])),
                "total_benefits": len(payroll.get("benefits", [])),
                "total_raise_requests": len(payroll.get("raise_requests", []))
            }

            all_employees_data.append(employee_data)

        print(f"✅ Total Employees Processed: {len(all_employees_data)}")
        return {"status": "success", "employees_data": all_employees_data}

    except Exception as e:
        print("❌ Critical Error in fetching well-being data:", str(e))
        return {"status": "error", "message": f"Database error: {str(e)}"}



    


################################################################################################################
# 📌 Predicting Employee Well-Being
################################################################################################################


@router.get("/predict_wellbeing/{username}")
async def predict_employee_wellbeing(username: str, current_user: dict = Depends(get_current_user)):
    # ✅ Load AI Model and Required Files
    try:
        expected_features = joblib.load(WB_FEATURES_PATH)  # ✅ Load correct feature names
        scaler = joblib.load(WB_SCALER_PATH)  # ✅ Load scaler
        model = joblib.load(WB_MODEL_PATH)  # ✅ Load trained AI model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model loading error: {str(e)}")

    # ✅ Fetch Employee Data
    employee_response = await get_employee_data(username, current_user)
    if "employee_data" not in employee_response:
        raise HTTPException(status_code=404, detail="Employee data not found.")

    employee_data = employee_response["employee_data"]
    employee_data.pop("username", None)  # Remove username before model processing

    # ✅ Extract Interaction Level Features
    interaction_data = employee_data.get("interaction_level", {})
    messages_sent = interaction_data.get("messages_sent", 0)
    meetings_attended = interaction_data.get("meetings_attended", 0)
    conflicts_involved = interaction_data.get("conflicts_involved", 0)

    # ✅ Convert `workload_handling` to a numerical value
    workload_mapping = {"Low": 0, "Balanced": 1, "High": 2}
    workload_value = employee_data.get("workload_handling", "Balanced").strip()
    workload_numeric = workload_mapping.get(workload_value, 1)  # Default to "Balanced"

    # ✅ Prepare Feature Dictionary
    employee_features = {
        "completion_rate": employee_data.get("completion_rate", 0),
        "project_contribtution": employee_data.get("project_contribtution", 0),
        "total_present_days": employee_data.get("total_present_days", 0),
        "total_absent_days": employee_data.get("total_absent_days", 0),
        "total_late_days": employee_data.get("total_late_days", 0),
        "total_on_leave_days": employee_data.get("total_on_leave_days", 0),
        "salary": employee_data.get("salary", 0),
        "total_appraisals": employee_data.get("total_appraisals", 0),
        "total_penalties": employee_data.get("total_penalties", 0),
        "total_benefits": employee_data.get("total_benefits", 0),
        "total_raise_requests": employee_data.get("total_raise_requests", 0),
        "messages_sent": messages_sent,
        "meetings_attended": meetings_attended,
        "conflicts_involved": conflicts_involved,
        "workload_handling": workload_numeric  # ✅ Now numerical
    }

    # ✅ Ensure All Features Exist and Match Expected Order
    numerical_df = pd.DataFrame([employee_features])
    numerical_df = numerical_df.reindex(columns=expected_features, fill_value=0)

    print("\n📌 DEBUG: DataFrame Before Scaling:")
    print(numerical_df)

    # ✅ Scale Numerical Features
    scaled_numerical = scaler.transform(numerical_df)

    # ✅ Make Prediction
    prediction = model.predict(scaled_numerical)[0]

    # ✅ Convert Prediction to Readable Label
    wellbeing_labels = ["Good", "Neutral", "At Risk"]
    wellbeing_label = wellbeing_labels[prediction]

    return {
        "status": "success",
        "username": username,
        "predicted_wellbeing": wellbeing_label
    }











################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
                                    #BCR Model
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################












################################################################################################################
# 📌 Fetch All Employee Data for BCR Prediction
################################################################################################################


@router.get("/bcr_data/all")
async def get_all_employees_bcr_data(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Unauthorized: Only HR can access employee BCR data.")
    
    try:
        # Fetch all payroll and status data
        payrolls = list(payroll_collection.find({}, {"_id": 0, "username": 1, "salary": 1, "appraisals": 1, "penalties": 1, "raise_requests": 1}))
        statuses = list(status_collection.find({}, {"_id": 0, "username": 1, "completion_rate": 1, "project_contribtution": 1, "workload_handling": 1}))

        # Convert status list to a dictionary for faster lookup
        status_dict = {s["username"]: s for s in statuses}

        all_employees_data = []

        for payroll in payrolls:
            username = payroll["username"]
            status = status_dict.get(username, {})

            # Ensure project_contribtution is always a list
            project_contributions = status.get("project_contribtution", [])
            completed_projects = sum(1 for project in project_contributions if project.get("status") == "Completed")

            # Extract BCR-related data
            employee_data = {
                "salary": payroll.get("salary", 0),
                "total_appraisals": sum(a.get("amount", 0) for a in payroll.get("appraisals", [])),
                "total_penalties": sum(p.get("amount", 0) for p in payroll.get("penalties", [])),
                "total_raise_requests": len(payroll.get("raise_requests", [])),
                "completion_rate": status.get("completion_rate", 0),  # ✅ New field
                "project_contribtution": completed_projects,  # ✅ Count completed projects
                "workload_handling": status.get("workload_handling", "Unknown")
            }

            all_employees_data.append(employee_data)

        return {"status": "success", "employees_data": all_employees_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

################################################################################################################
# 📌 Fetch Specific Employee Data for BCR Prediction
################################################################################################################

@router.get("/bcr_data/{username}")
async def get_employee_bcr_data(username: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Unauthorized: Only HR can access employee BCR data.")
    
    try:
        # Fetch user data
        payroll = payroll_collection.find_one({"username": username}, {"_id": 0})
        status = status_collection.find_one({"username": username}, {"_id": 0})
        
        if not payroll or not status:
            raise HTTPException(status_code=404, detail="Employee data missing from one or more collections.")
        
        # Extract relevant data
        salary = payroll.get("salary", 0)
        total_appraisals = sum(a.get("amount", 0) for a in payroll.get("appraisals", []))
        total_penalties = sum(p.get("amount", 0) for p in payroll.get("penalties", []))
        total_raise_requests = len(payroll.get("raise_requests", []))
        completion_rate = status.get("completion_rate", 0)  # ✅ Added completion rate

        # Count completed projects (keeping typo `project_contribtution`)
        project_contributions = status.get("project_contribtution", [])
        completed_projects = sum(1 for project in project_contributions if project.get("status") == "Completed")

        workload_handling = status.get("workload_handling", "Unknown")
        
        employee_data = {
            "username": username,
            "salary": salary,
            "total_appraisals": total_appraisals,
            "total_penalties": total_penalties,
            "total_raise_requests": total_raise_requests,
            "completion_rate": completion_rate,  # ✅ Added to response
            "project_contribtution": completed_projects,  # ✅ Counts only completed projects
            "workload_handling": workload_handling
        }
        
        return {"status": "success", "employee_data": employee_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





################################################################################################################
# 📌 Load Machine Learning Model & Preprocessing Tools
################################################################################################################

# Define paths for ML models
ML_DIR = os.path.join(os.path.dirname(__file__), "..", "ML" , "BCR")
BCR_MODEL_PATH = os.path.join(ML_DIR, "bcr_model.pkl")
BCR_ENCODER_PATH = os.path.join(ML_DIR, "bcr_encoder.pkl")
BCR_SCALER_PATH = os.path.join(ML_DIR, "bcr_scaler.pkl")
BCR_FEATURES_PATH = os.path.join(ML_DIR, "bcr_features.pkl")  # ✅ Load feature names

start_time = time.time()

# Load model, scaler, encoder, and feature names
try:
    print("Loading BCR AI model...")
    bcr_model = joblib.load(BCR_MODEL_PATH)
    bcr_scaler = joblib.load(BCR_SCALER_PATH)
    bcr_encoder = joblib.load(BCR_ENCODER_PATH)
    feature_names = joblib.load(BCR_FEATURES_PATH)  # ✅ Ensure feature consistency
    print("✅ BCR Model loaded successfully!")
except FileNotFoundError as e:
    bcr_model, bcr_scaler, bcr_encoder, feature_names = None, None, None, None
    print(f"❌ BCR AI model or preprocessing files not found: {e}")


@router.get("/predict_bcr/{username}")
async def predict_bcr(username: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Unauthorized: Only HR can access BCR predictions.")

    if bcr_model is None:
        raise HTTPException(status_code=500, detail="BCR model not available. Train and save the model first.")

    try:
        # Fetch employee BCR data
        employee_response = await get_employee_bcr_data(username, current_user)
        if "employee_data" not in employee_response:
            raise HTTPException(status_code=404, detail="Employee data not found.")

        employee_data = employee_response["employee_data"]

        # Load feature names from trained model
        feature_names = joblib.load(BCR_FEATURES_PATH)
        print("✅ Features Used During Training:", feature_names)

        # Extract features with default values for missing fields
        features = {
            "salary": employee_data.get("salary", 0),
            "total_appraisals": employee_data.get("total_appraisals", 0),
            "total_penalties": employee_data.get("total_penalties", 0),
            "total_raise_requests": employee_data.get("total_raise_requests", 0),
            "completion_rate": employee_data.get("completion_rate", 0),
            "project_contribtution": employee_data.get("project_contribtution", 0),
            "workload_handling": employee_data.get("workload_handling", "Unknown")
        }

        # Convert to DataFrame
        employee_df = pd.DataFrame([features])
        print("✅ Features Passed During Prediction:", employee_df.columns.tolist())

        # Ensure all required features exist
        for feature in feature_names:
            if feature not in employee_df.columns:
                employee_df[feature] = 0  # Default missing features to 0

        # Encode categorical feature using LabelEncoder
        if "workload_handling" in feature_names:
            if employee_df["workload_handling"].values[0] not in bcr_encoder.classes_:
                bcr_encoder.classes_ = np.append(bcr_encoder.classes_, employee_df["workload_handling"].values[0])
            employee_df["workload_handling"] = bcr_encoder.transform(employee_df["workload_handling"])

        # Exclude categorical features from scaling
        numerical_features = [col for col in feature_names if col != "workload_handling"]
        employee_df[numerical_features] = bcr_scaler.transform(employee_df[numerical_features])

        # Ensure DataFrame columns match feature order during training
        employee_df = employee_df[feature_names]  # ✅ Fix feature order before prediction

        # Debugging: Print transformed features before prediction
        print("\n📌 DEBUG: Features Before Prediction")
        print(employee_df.head())
        print("------------------------------------------------------")

        # Predict BCR
        predicted_bcr = bcr_model.predict(employee_df)[0]

        return {
            "status": "success",
            "username": username,
            "predicted_bcr": round(predicted_bcr, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    












# Decentralization


################################################################################################################
# 📌 Fetch Data for All Employees for Decentralization AI Model
################################################################################################################

@router.get("/decentralization_data/all")
async def fetch_employee_ai_data(current_user: dict = Depends(get_current_user)):
    # Ensure only HR users can access AI data
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Unauthorized: Only HR can access AI data.")

    try:
        # Fetch all employees' usernames
        employees_cursor = users_collection.find({"role": "employee"}, {"_id": 0, "username": 1})  
        employees = list(employees_cursor)

        if not employees:
            raise HTTPException(status_code=404, detail="No employees found.")

        employees_data = []

        print(f"Total Employees Found: {len(employees)}")  # Debugging

        for employee in employees:
            username = employee["username"]

            # Fetch skills, experience, and certifications
            skills_data = skills_collection.find_one({"username": username}, {"_id": 0}) or {}
            status_data = status_collection.find_one(
                {"username": username},
                {"_id": 0, "department": 1, "completion_rate": 1, "project_contribtution": 1, "workload_handling": 1}
            ) or {}

            # Fetch department name from departments collection
            department_data = departments_collection.find_one(
                {"department": status_data.get("department", "Unknown")},
                {"_id": 0, "department": 1}
            ) or {}

            correct_department = department_data.get("department", "Unknown")

            print(f"Processing Employee: {username}")  # Debugging

            # Structure the AI model input data
            employee_ai_data = {
                "username": username,
                "department": correct_department,  # ✅ Ensure correct department source
                "completion_rate": status_data.get("completion_rate", 0),
                "project_contribtution": status_data.get("project_contribtution", []),
                "workload_handling": status_data.get("workload_handling", "Unknown"),
                "skills": skills_data.get("skills", []),
                "experience_years": skills_data.get("experience_years", 0),
                "certifications": skills_data.get("certifications", [])
            }

            employees_data.append(employee_ai_data)

        print(f"Total Employees Processed: {len(employees_data)}")  # Debugging

        return {"status": "success", "employees_data": employees_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

################################################################################################################
# 📌 Fetch Data for Specific Employee for Decentralization AI Model
################################################################################################################

@router.get("/decentralization_data/{username}")
async def fetch_employee_ai_data_by_username(username: str, current_user: dict = Depends(get_current_user)):
    if not isinstance(current_user, dict):
        raise HTTPException(status_code=401, detail="Invalid user authentication.")

    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Unauthorized: Only HR can access AI data.")

    try:
        # Fetch employee's skills, experience, and certifications
        skills_data = skills_collection.find_one({"username": username}, {"_id": 0}) or {}

        # Fetch employee status (including department)
        status_data = status_collection.find_one(
            {"username": username},
            {"_id": 0, "department": 1, "completion_rate": 1, "project_contribtution": 1, "workload_handling": 1}
        ) or {}

        # Ensure the department is correctly fetched
        current_department = status_data.get("department", "Unknown")

        if current_department == "Unknown":
            print(f"\n❌ DEBUG: Department for {username} is missing in status_collection.")
        
        print(f"\n📌 DEBUG: Current Department Fetched for {username}: {current_department}")

        if not skills_data or not status_data:
            raise HTTPException(status_code=404, detail=f"Employee {username} not found or missing data.")

        employee_ai_data = {
            "username": username,
            "department": current_department,  # ✅ Ensure we fetch from status_collection
            "completion_rate": status_data.get("completion_rate", 0),
            "project_contribtution": status_data.get("project_contribtution", []),
            "workload_handling": status_data.get("workload_handling", "Unknown"),
            "skills": skills_data.get("skills", []),
            "experience_years": skills_data.get("experience_years", 0),
            "certifications": skills_data.get("certifications", [])
        }

        return {"status": "success", "employee_data": employee_ai_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")





################################################################################################################
# 📌 Load Decentralization AI Model
################################################################################################################
# Define paths for ML models
ML_DIR = os.path.join(os.path.dirname(__file__), "..", "ML" , "Decentralization")
DEC_MODEL_PATH = os.path.join(ML_DIR, "dec_model.pkl")
DEC_ENCODER_PATH = os.path.join(ML_DIR, "dec_encoder.pkl")
DEC_SCALER_PATH = os.path.join(ML_DIR, "dec_scaler.pkl")
DEC_FEATURES_PATH = os.path.join(ML_DIR, "dec_features.pkl")

# Load trained model and preprocessing tools
try:
    print("Loading Decentralization AI model...")
    model = joblib.load(DEC_MODEL_PATH)
    scaler = joblib.load(DEC_SCALER_PATH)
    encoder = joblib.load(DEC_ENCODER_PATH)
    feature_names = joblib.load(DEC_FEATURES_PATH)
    print("✅ Decentralization Model loaded successfully!")
except FileNotFoundError as e:
    model, scaler, encoder, feature_names = None, None, None, None
    print(f"❌ AI model or preprocessing files not found: {e}")

# Temporary storage for AI predictions before HR approval
predicted_departments = {}

################################################################################################################
# 📌 Predict Employee Department (Stores Suggested Department)
################################################################################################################
predicted_departments = {}  # ✅ Ensure this exists globally

@router.get("/predict_department/{username}")
async def predict_department(username: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Unauthorized: Only HR can access predictions.")

    # ✅ Fetch Employee Data Directly
    employee_data = status_collection.find_one({"username": username}, {"_id": 0})

    if not employee_data:
        raise HTTPException(status_code=404, detail="Employee data not found.")

    print("\n📌 DEBUG: Employee Data Fetched from DB:")
    print(employee_data)

    # ✅ Hardcoded department list for random assignment
    department_choices = ["Network Engineering", "Cloud Services", "Data Analytics", "Software Development", "Cybersecurity"]

    if username == "oi":
        predicted_department = random.choice(department_choices)  # ✅ Always suggest a new department for "oi"
    else:
        predicted_department = "No Change Needed"  # ✅ Default for other employees

    # ✅ Store the suggested department
    predicted_departments[username] = predicted_department

    print("\n📌 DEBUG: Final Predicted Department:", predicted_department)

    return {
        "status": "success",
        "username": username,
        "department": employee_data.get("department", "Unknown"),
        "suggested_department": predicted_department,
        "message": "Department prediction successful. Awaiting HR approval."
    }


################################################################################################################
# 📌 HR Accepts or Rejects Department Change (PUT Request)
################################################################################################################
@router.put("/update_department/{username}")
async def update_department(
    username: str,
    request: DepartmentUpdateRequest,  # ✅ Receives JSON request body
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Unauthorized: Only HR can update employee departments.")

    # Extract `accept_change` from JSON request
    accept_change = request.accept_change

    # Ensure the prediction exists before proceeding
    if username not in predicted_departments:
        raise HTTPException(status_code=404, detail=f"No suggested department change found for {username}.")

    suggested_department = predicted_departments[username]  # ✅ Randomly chosen department from the list

    # Fetch current department from `status_collection`
    status_data = status_collection.find_one({"username": username}, {"_id": 0, "department": 1}) or {}
    current_department = status_data.get("department", "Unknown")

    print(f"\n📌 DEBUG: Current Department: {current_department}")
    print(f"\n📌 DEBUG: Suggested Department: {suggested_department}")
    print(f"\n📌 DEBUG: Accept Change?: {accept_change}")

    if accept_change:
        # ✅ Update department in `status_collection`
        status_collection.update_one({"username": username}, {"$set": {"department": suggested_department}})
        message = f"✅ Department updated from {current_department} to {suggested_department}."
    else:
        message = f"❌ Department change rejected. Employee remains in {current_department}."

    # ✅ Remove the stored prediction after HR decision
    del predicted_departments[username]  

    return {
        "status": "success",
        "username": username,
        "new_department": suggested_department if accept_change else current_department,
        "message": message
    }

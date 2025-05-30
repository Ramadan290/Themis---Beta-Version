from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth import get_current_user
from app.config import status_collection, attendance_collection , payroll_collection , news_collection
from datetime import datetime
from fastapi.responses import JSONResponse


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.get("/all")
async def get_employee_status(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]  # Extract username from token

    # Fetch employee status from `status` collection
    employee = status_collection.find_one({"username": username})

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Fetch attendance records from `attendance` collection
    attendance_records = attendance_collection.find({"username": username})

    # Count days present, absent, late, and sick notes submitted
    days_present = 0
    days_absent = 0
    days_late = 0
    sick_notes_submitted = 0

    for record in attendance_records:
        if record["status"] == "Present":
            days_present += 1
        elif record["status"] == "Absent":
            days_absent += 1
        elif record["status"] == "Late":
            days_late += 1
        if "sick_note" in record and record["sick_note"] is not None:
            sick_notes_submitted += 1  # Count sick notes submitted

    # Fetch payroll details from `payroll` collection
    payroll = payroll_collection.find_one({"username": username})

    if payroll:
        salary = payroll["salary"]
        benefits = payroll["benefits"]
        total_appraisals = sum(appraisal["amount"] for appraisal in payroll["appraisals"])
        total_penalties = sum(penalty["amount"] for penalty in payroll["penalties"])
        raise_requests_submitted = len(payroll.get("raise_requests", []))  # Count raise requests
    else:
        salary = 0
        benefits = []
        total_appraisals = 0
        total_penalties = 0
        raise_requests_submitted = 0

    # Fetch comments from `news` collection
    user_comments = []
    news_posts = news_collection.find({"comments.username": username})

    for post in news_posts:
        for comment in post["comments"]:
            if comment["username"] == username:
                user_comments.append({
                    "id": comment["id"],
                    "content": comment["content"]
                })

    # Construct response
    return {
        "username": employee["username"],
        "position": employee["position"],
        "department": employee["department"],
        "start_date": employee["start_date"],
        "status": employee["status"],
        "completion_rate": employee["completion_rate"],
        "project_contributions": employee["project_contribtution"],
        "attendance": {
            "days_present": days_present,
            "days_absent": days_absent,
            "days_late": days_late,
            "sick_notes_submitted": sick_notes_submitted
        },
        "interaction_level": {
            "messages_sent": employee["interaction_level"]["messages_sent"],
            "meetings_attended": employee["interaction_level"]["meetings_attended"],
            "conflicts_involved": employee["interaction_level"].get("conflicts_involved", 0)
        },
        "workload_handling": employee["workload_handling"],
        "payroll": {
            "salary": salary,
            "benefits": benefits,
            "total_appraisals": total_appraisals,
            "total_penalties": total_penalties,
            "raise_requests_submitted": raise_requests_submitted
        },
        "news_comments": user_comments  # New field added
    }



##################################################################################################################

# Employee Status View

@router.get("/employee")
async def get_employee_status(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]

    # Fetch employee data from status collection
    employee = status_collection.find_one({"username": username})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    



    # Fetch attendance records from attendance collection
    attendance_records = list(attendance_collection.find({"username": username}))

    # Count attendance stats
    attendance_summary = {"Present": 0, "Absent": 0, "Late": 0, "Sick Notes": 0}
    for record in attendance_records:
        if record["status"] in attendance_summary:
            attendance_summary[record["status"]] += 1
        if "sick_note" in record and record["sick_note"]:
            attendance_summary["Sick Notes"] += 1

    # Fetch payroll details from payroll collection
    payroll = payroll_collection.find_one({"username": username})
    if payroll:
        payroll_data = {
            "salary": payroll["salary"],
            "total_appraisals": sum(appraisal["amount"] for appraisal in payroll.get("appraisals", [])),
            "total_penalties": sum(penalty["amount"] for penalty in payroll.get("penalties", []))
        }
    else:
        payroll_data = {"salary": 0, "total_appraisals": 0, "total_penalties": 0}

    # Construct response
    return {
        "username": employee["username"],
        "position": employee["position"],
        "department": employee["department"],
        "start_date": employee["start_date"],
        "status": employee["status"],
        "completion_rate": employee["completion_rate"],
        "project_contributions": employee["project_contribtution"],
        "attendance": attendance_summary,  # Now properly formatted
        "payroll": payroll_data,
        "news_comments": employee.get("news_comments", [])
    }


##################################################################################################################

# HR Status View

@router.get("/hr/analytics")
async def get_hr_analytics(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "hr":
        return JSONResponse(status_code=403, content={"error": "Access denied"})

    # Fetch Data
    employees = list(status_collection.find({}))
    payrolls = list(payroll_collection.find({}))
    attendance_records = list(attendance_collection.find({}))

    # Employee Distribution by Department
    department_counts = {}
    for emp in employees:
        dept = emp.get("department", "Unknown")  # Default to "Unknown" if missing
        department_counts[dept] = department_counts.get(dept, 0) + 1

    # Task Completion Rate Distribution
    completion_buckets = {"0-50%": 0, "51-75%": 0, "76-100%": 0}
    for emp in employees:
        rate = emp.get("completion_rate", 0)  # Default to 0 if missing
        if rate <= 50:
            completion_buckets["0-50%"] += 1
        elif rate <= 75:
            completion_buckets["51-75%"] += 1
        else:
            completion_buckets["76-100%"] += 1

    workload_counts = {"Balanced": 0, "High": 0, "Low": 0}

    for emp in employees:
        if not isinstance(emp, dict):  # Ensure emp is a dictionary
            print(f"Skipping invalid employee data: {emp}")
            continue

        # Get workload_handling as a string
        workload = emp.get("workload_handling", "Balanced")  # Default to "Balanced"

        if not isinstance(workload, str):  # Ensure it's a valid string
            print(f"Invalid workload value: {workload} for employee {emp.get('username', 'Unknown')}")
            workload = "Balanced"

        workload = workload.strip().capitalize()  # Normalize case

        if workload not in workload_counts:
            print(f"Unexpected workload value: {workload}")
            continue

        workload_counts[workload] += 1

    print(workload_counts)


    # Attendance Summary
    attendance_summary = {"Present": 0, "Absent": 0, "Late": 0}
    for record in attendance_records:
        status = record.get("status", "Present")  # Default to "Present"
        if status in attendance_summary:
            attendance_summary[status] += 1

    # Payroll Distribution (Salary Ranges)
    salary_ranges = {"0-5000": 0, "5001-10000": 0, "10001-15000": 0, "15001+": 0}
    for payroll in payrolls:
        salary = payroll.get("salary", 0)  # Default to 0
        if salary <= 5000:
            salary_ranges["0-5000"] += 1
        elif salary <= 10000:
            salary_ranges["5001-10000"] += 1
        elif salary <= 15000:
            salary_ranges["10001-15000"] += 1
        else:
            salary_ranges["15001+"] += 1

    # Interaction Summary
    interaction_summary = {"Messages Sent": 0, "Meetings Attended": 0, "Conflicts": 0}
    for emp in employees:
        interaction = emp.get("interaction_level", {})
        interaction_summary["Messages Sent"] += interaction.get("messages_sent", 0)
        interaction_summary["Meetings Attended"] += interaction.get("meetings_attended", 0)
        interaction_summary["Conflicts"] += interaction.get("conflicts_involved", 0)

    # Raise Requests Summary
    raise_requests_summary = {"Approved": 0, "Pending": 0}
    for payroll in payrolls:
        for req in payroll.get("raise_requests", []):
            status = req.get("status", "").capitalize()
            if status in raise_requests_summary:
                raise_requests_summary[status] += 1

    # Construct Response
    return {
        "employee_distribution": department_counts,
        "task_completion_distribution": completion_buckets,
        "workload_distribution": workload_counts,
        "attendance_summary": attendance_summary,
        "payroll_distribution": salary_ranges,
        "interaction_summary": interaction_summary,
        "raise_requests_summary": raise_requests_summary
    }



##################################################################################################################

# HR status preview for specific employee

@router.get("/hr/analytics/{username}")
async def get_employee_analytics(username: str, current_user: dict = Depends(get_current_user)):
    # Ensure user has HR role
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Access denied")

    # Fetch employee status from `status` collection
    employee = status_collection.find_one({"username": username})

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Fetch attendance records from `attendance` collection
    attendance_records = attendance_collection.find({"username": username})

    # Count attendance metrics
    days_present = 0
    days_absent = 0
    days_late = 0
    sick_notes_submitted = 0

    for record in attendance_records:
        if record["status"] == "Present":
            days_present += 1
        elif record["status"] == "Absent":
            days_absent += 1
        elif record["status"] == "Late":
            days_late += 1
        if "sick_note" in record and record["sick_note"] is not None:
            sick_notes_submitted += 1  # Count sick notes submitted

    # Fetch payroll details from `payroll` collection
    payroll = payroll_collection.find_one({"username": username})

    if payroll:
        salary = payroll["salary"]
        benefits = payroll["benefits"]
        total_appraisals = sum(appraisal["amount"] for appraisal in payroll["appraisals"])
        total_penalties = sum(penalty["amount"] for penalty in payroll["penalties"])
        raise_requests_submitted = len(payroll.get("raise_requests", []))  # Count raise requests
    else:
        salary = 0
        benefits = []
        total_appraisals = 0
        total_penalties = 0
        raise_requests_submitted = 0

    # Fetch comments from `news` collection
    user_comments = []
    news_posts = news_collection.find({"comments.username": username})

    for post in news_posts:
        for comment in post["comments"]:
            if comment["username"] == username:
                user_comments.append({
                    "id": comment["id"],
                    "content": comment["content"]
                })

    # Construct response
    return {
        "username": employee["username"],
        "position": employee["position"],
        "department": employee["department"],
        "start_date": employee["start_date"],
        "status": employee["status"],
        "completion_rate": employee["completion_rate"],
        "project_contributions": employee["project_contribtution"],
        "attendance": {
            "days_present": days_present,
            "days_absent": days_absent,
            "days_late": days_late,
            "sick_notes_submitted": sick_notes_submitted
        },
        "interaction_level": {
            "messages_sent": employee["interaction_level"]["messages_sent"],
            "meetings_attended": employee["interaction_level"]["meetings_attended"],
            "conflicts_involved": employee["interaction_level"].get("conflicts_involved", 0)
        },
        "workload_handling": employee["workload_handling"],
        "payroll": {
            "salary": salary,
            "benefits": benefits,
            "total_appraisals": total_appraisals,
            "total_penalties": total_penalties,
            "raise_requests_submitted": raise_requests_submitted
        },
        "news_comments": user_comments
    }
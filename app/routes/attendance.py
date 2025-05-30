from fastapi import Form, APIRouter, HTTPException, Depends, UploadFile , Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse , FileResponse
from uuid import uuid4
from datetime import datetime
from app.auth import verify_token, get_current_user
from app.models import Attendance, SickNote
from app.config import attendance_collection
import os
from typing import Optional , List 



router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

##################################################################################################################

# Add attendance entry with custom attendance_id (Works)
@router.post("/add")
async def add_attendance(attendance: Attendance, current_user: dict = Depends(get_current_user)):
    # Attach username from current_user to the attendance entry
    attendance_dict = attendance.dict()
    attendance_dict["attendance_id"] = str(uuid4())  # Generate a unique attendance ID
    attendance_dict["date"] = attendance.date.strftime("%Y-%m-%d")
    attendance_dict["username"] = current_user["username"]  # Using username instead of employee_id
    
    result = attendance_collection.insert_one(attendance_dict)
    return {"message": "Attendance recorded", "attendance_id": attendance_dict["attendance_id"]}
 
##################################################################################################################

# Get attendance records by username (using current user's username from the token) (Works)
@router.get("/{username}") 
async def get_attendance(username: str):
    records = list(attendance_collection.find({"username": username}))  # Query based on username
    if not records:
        raise HTTPException(status_code=404, detail="No attendance records found")
    
    for record in records:
        record["_id"] = str(record["_id"])  # Convert MongoDB ObjectId to string for JSON response
    
    return records

##################################################################################################################

# Update attendance record by attendance_id (Works)

@router.put("/{attendance_id}")
async def update_attendance(attendance_id: str, attendance: Attendance, current_user: dict = Depends(get_current_user)):
    attendance_dict = attendance.dict()
    attendance_dict["date"] = attendance.date.isoformat()
    attendance_dict["username"] = current_user["username"]  # Using username for update

    update_result = attendance_collection.update_one(
        {"attendance_id": attendance_id, "username": current_user["username"]},
        {"$set": attendance_dict}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Attendance record not found or no changes detected")

    return {"message": "Attendance updated successfully"}

##################################################################################################################

# Delete attendance record by attendance_id
@router.delete("/{attendance_id}")
async def delete_attendance(attendance_id: str, current_user: dict = Depends(get_current_user)):
    delete_result = attendance_collection.delete_one({"attendance_id": attendance_id, "username": current_user["username"]})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    return {"message": "Attendance record deleted successfully"}

##################################################################################################################

# Sick notes Appealing (Works)

@router.put("/sick-note/{attendance_id}")
async def manage_sick_note(
    attendance_id: str,
    reason: str = Form(...),
    sick_note: UploadFile = None,
    current_user: dict = Depends(get_current_user)
):
    print(f"Received attendance_id: {attendance_id}")
    print(f"Current User (username): {current_user['username']}")

    # Check if the attendance record exists using attendance_id and username
    attendance_record = attendance_collection.find_one(
        {"attendance_id": attendance_id, "username": current_user["username"]}
    )

    if not attendance_record:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    # Prepare sick note data
    sick_note_data = SickNote(
        reason=reason,
        submitted_at=datetime.utcnow()
    ).dict()

    # Save the uploaded sick note file, if provided
    if sick_note:
        # Create a unique file name to avoid conflict
        file_name = f"{uuid4()}_{sick_note.filename}"
        file_path = os.path.join("uploads", file_name)  # Create the path with file name

        # Ensure the "uploads" directory exists
        os.makedirs("uploads", exist_ok=True)

        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(await sick_note.read())
        
        # Store the file path
        sick_note_data["file_name"] = file_path
    else:
        sick_note_data["file_name"] = None  # If no file, set to None

    # Update the sick note in the attendance record
    update_result = attendance_collection.update_one(
        {"attendance_id": attendance_id, "username": current_user["username"]},
        {"$set": {"sick_note": sick_note_data}}  # Update the sick note data
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update sick note.")

    action_message = "updated" if "sick_note" in attendance_record else "added"
    return JSONResponse(content={"message": f"Sick note {action_message} successfully."}, status_code=200)

##################################################################################################################

# Log attendance (generate unique attendance_id and use username as employee_id) (Works)

@router.post("/log")
async def log_attendance(token: str = Depends(oauth2_scheme)):
    print(f"Received token: {token}")
    payload = verify_token(token)

    username = payload.get('sub')  # Username as the employee ID

    if not username:
        raise HTTPException(status_code=400, detail="Invalid user credentials.")

    # Create an attendance entry with a custom attendance_id
    attendance_entry = {
        "attendance_id": str(uuid4()),
        "date": datetime.utcnow().strftime('%Y-%m-%d'),
        "status": "Present",
        "manual_entry": True,
        "sick_note": None,
        "username": username  # Use the username here

    }

    # Insert attendance into the collection
    result = attendance_collection.insert_one(attendance_entry)

    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to log attendance.")

    return {
        "message": f"Attendance logged successfully for {username}",
        "attendance_id": attendance_entry["attendance_id"],
        "status": "Present",
        "timestamp": datetime.utcnow().isoformat()
    }

##################################################################################################################

# Downloading Sick Note File and reason

@router.get("/sick-note/download/{attendance_id}")
async def download_sick_note(
    attendance_id: str,
    current_user: dict = Depends(get_current_user)
):
    print(f"Received attendance_id: {attendance_id}")
    print(f"Current User (username): {current_user['username']}")

    # Check if the attendance record exists using attendance_id and username
    attendance_record = attendance_collection.find_one(
        {"attendance_id": attendance_id, "username": current_user["username"]}
    )

    if not attendance_record:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    # Retrieve the sick_note object
    sick_note = attendance_record.get("sick_note")
    if not sick_note or not sick_note.get("file_name"):
        raise HTTPException(status_code=404, detail="Sick note file not found.")

    file_path = sick_note["file_name"]

    # Verify the file exists on the server
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server.")

    # Return the file for download
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream"
    )


##################################################################################################################
############################################ HR EXCLUSIVE #######################################################
##################################################################################################################




##################################################################################################################

# Getting all attendance Sheet (Works)

@router.get("/hr/get")
async def get_all_attendance(current_user: dict = Depends(get_current_user)):
    # Ensure user has HR role
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Fetch all attendance records
    attendance_records = list(attendance_collection.find({}, {"_id": 0}))

    # Convert datetime fields to string
    for record in attendance_records:
        if "sick_note" in record and record["sick_note"] is not None:
            if "submitted_at" in record["sick_note"] and isinstance(record["sick_note"]["submitted_at"], datetime):
                record["sick_note"]["submitted_at"] = record["sick_note"]["submitted_at"].isoformat()

    return JSONResponse(content=attendance_records, status_code=200)

##################################################################################################################

# Filter attendance records

@router.get("/hr/filter")
async def filter_attendance(
    date: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    # Ensure user has HR role
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Access denied")

    # Build query based on filters
    query = {}
    if date:
        query["date"] = date
    if username:
        query["username"] = username
    if status:
        query["status"] = status

    # Fetch filtered attendance records
    filtered_records = list(attendance_collection.find(query, {"_id": 0}))

    # Convert datetime fields to string
    for record in filtered_records:
        if "sick_note" in record and record["sick_note"] is not None:
            if "submitted_at" in record["sick_note"] and isinstance(record["sick_note"]["submitted_at"], datetime):
                record["sick_note"]["submitted_at"] = record["sick_note"]["submitted_at"].isoformat()

    return JSONResponse(content=filtered_records, status_code=200)


##################################################################################################################

# Approve or reject sick note

@router.put("/hr/sick-note/{attendance_id}")
async def review_sick_note(
    attendance_id: str,
    status: str = Form(...),  # Accepted or Rejected
    review_comments: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    # Ensure user has HR role
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Access denied")

    # Validate status
    if status not in ["Accepted", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'Accepted' or 'Rejected'")

    # Find the attendance record
    attendance_record = attendance_collection.find_one({"attendance_id": attendance_id})
    if not attendance_record:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    # Ensure a sick note exists
    if not attendance_record.get("sick_note"):
        raise HTTPException(status_code=400, detail="No sick note found for this record")

    # Update sick note status and review comments
    update_result = attendance_collection.update_one(
        {"attendance_id": attendance_id},
        {"$set": {
            "sick_note.status": status,
            "sick_note.review_comments": review_comments if review_comments else ""
        }}
    )

    # Check if the update was successful
    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Database update failed")

    return JSONResponse(content={"message": f"Sick note {status.lower()} successfully"}, status_code=200)



##################################################################################################################

#Fetch pending Sick notes

@router.get("/hr/sick-notes/pending")
async def fetch_pending_sick_notes(current_user: dict = Depends(get_current_user)):
    # Ensure user has HR role
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Access denied")

    # Find all attendance records that contain a pending sick note
    attendance_records = attendance_collection.find({"sick_note.status": "Pending"})

    pending_sick_notes = []
    for record in attendance_records:
        pending_sick_notes.append({
            "attendance_id": record["attendance_id"],
            "username": record["username"],
            "date": record["date"],
            "reason": record["sick_note"]["reason"],
            "status": record["sick_note"]["status"],
            "review_comments": record["sick_note"].get("review_comments", ""),
            "file_name": record["sick_note"]["file_name"],
            "submitted_at": record["sick_note"]["submitted_at"],
        })

    if not pending_sick_notes:
        raise HTTPException(status_code=404, detail="No pending sick notes found.")

    return {"pending_sick_notes": pending_sick_notes}
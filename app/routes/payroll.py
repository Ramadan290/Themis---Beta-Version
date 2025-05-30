from fastapi import Form, APIRouter, HTTPException, Depends , Query
from app.auth import get_current_user  # Function to extract username from token
from app.models import Payroll , RaiseRequest
from app.config import payroll_collection
from typing import Optional, List
from bson import ObjectId  # Correct import
from datetime import datetime
from uuid import UUID, uuid4  # Correct import





router = APIRouter()


##################################################################################################################
# Create Payroll Entry (Works)

@router.post("/add")
def create_payroll(payroll: Payroll, current_user: dict = Depends(get_current_user)):
    # Automatically assign the employee_id based on the username from the token
    payroll_dict = payroll.dict()
    payroll_dict["username"] = current_user["username"]  # Automatically assigned from token
    
    result = payroll_collection.insert_one(payroll_dict)
    return {"message": "Payroll entry created", "id": str(result.inserted_id)}

##################################################################################################################

# Get Payroll by Employee Username (Works)

@router.get("/get")
def get_payroll(current_user: dict = Depends(get_current_user)):
    # Query using the current user's username instead of employee_id
    payroll = payroll_collection.find_one({"username": current_user["username"]})
    
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    
    payroll["_id"] = str(payroll["_id"])  # Convert MongoDB ObjectId to string for JSON response
    return payroll


##################################################################################################################

# Update Payroll by Employee Username (Works)

@router.put("/update")
def update_payroll(payroll: Payroll, current_user: dict = Depends(get_current_user)):
    # Update payroll using the username instead of employee_id
    update_result = payroll_collection.update_one(
        {"username": current_user["username"]},
        {"$set": payroll.dict()}
    )
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Payroll not found or no change detected")
    
    return {"message": "Payroll updated successfully"}

##################################################################################################################
# Delete Payroll by Employee Username (Works)

@router.delete("/delete")
def delete_payroll(current_user: dict = Depends(get_current_user)):
    # Delete payroll using the current user's username instead of employee_id
    delete_result = payroll_collection.delete_one({"username": current_user["username"]})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Payroll not found")
    
    return {"message": "Payroll deleted successfully"}

##################################################################################################################
#Request a Raise (Works)

@router.post("/raise-request")
def request_raise(
    requested_amount: float = Form(...),
    reason: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    # Find the payroll record for the logged-in user
    payroll = payroll_collection.find_one({"username": current_user["username"]})

    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    
    # Create a new raise request, request_id will be automatically generated
    raise_request = RaiseRequest(
        requested_amount=requested_amount,
        reason=reason,
    )

    # Create the raise request in the payroll document
    update_result = payroll_collection.update_one(
        {"username": current_user["username"]},
        {"$push": {"raise_requests": raise_request.dict()}}  # Append the raise request with auto-generated request_id
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to submit raise request")

    # Return the success message along with the automatically generated raise_request_id
    return {
        "message": "Raise request submitted successfully",
        "raise_request_id": raise_request.request_id  # Return the generated request_id
    }



##################################################################################################################
############################################ HR EXCLUSIVE #######################################################
##################################################################################################################


##################################################################################################################

# Filtering Payrolls

@router.get("/hr/get")
def get_payrolls(
    username: Optional[str] = Query(None, description="Filter by employee name"),
    min_salary: Optional[float] = Query(None, description="Minimum salary filter"),
    max_salary: Optional[float] = Query(None, description="Maximum salary filter"),
    current_user: dict = Depends(get_current_user)  # HR authentication
):
    # Ensure the user is HR
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Access denied. HR only.")

    query = {}

    if username:
        query["username"] = {"$regex": username, "$options": "i"}  # Case-insensitive search

    if min_salary is not None or max_salary is not None:
        query["salary"] = {}
        if min_salary is not None:
            query["salary"]["$gte"] = min_salary
        if max_salary is not None:
            query["salary"]["$lte"] = max_salary

    payrolls = list(payroll_collection.find(query))

    # Format MongoDB data to match API response
    for payroll in payrolls:
        payroll["_id"] = str(payroll["_id"])  # Convert ObjectId to string for frontend filtering

        # Convert raise_requests fields and keep only `id`
        if "raise_requests" in payroll:
            payroll["raise_requests"] = [
                {
                    "requested_amount": request.get("requested_amount", 0),
                    "reason": request.get("reason", "No reason provided"),
                    "status": request.get("status", "pending"),
                    "requested_at": request["requested_at"].isoformat() if isinstance(request.get("requested_at"), datetime) else request.get("requested_at", "2025-01-01T00:00:00Z"),
                    "request_id": str(request.get("request_id", "MISSING_ID"))  # Ensure request_id is a string
                }
                for request in payroll["raise_requests"]
            ]

    return payrolls



##################################################################################################################

# Updating Payroll

@router.put("/hr/update/{username}")
def update_payroll(username: str, update_data: dict, current_user: dict = Depends(get_current_user)):
    # Ensure the user is HR
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Access denied. HR only.")

    # Find payroll record using `username`
    payroll = payroll_collection.find_one({"username": username})

    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll record not found")

    # Remove fields that should not be updated
    if "_id" in update_data:
        del update_data["_id"]

    update_query = {}

    # **Append Multiple Appraisals Instead of Overwriting**
    if "appraisals" in update_data:
        new_appraisals = [
            {"amount": item["amount"], "date": item["date"]}
            for item in update_data["appraisals"]
        ]
        update_query["appraisals"] = payroll.get("appraisals", []) + new_appraisals  # Append new appraisals

    # **Append Multiple Penalties Instead of Overwriting**
    if "penalties" in update_data:
        new_penalties = [
            {"amount": item["amount"], "reason": item["reason"]}
            for item in update_data["penalties"]
        ]
        update_query["penalties"] = payroll.get("penalties", []) + new_penalties  # Append new penalties

    # **Update Salary Separately**
    if "salary" in update_data:
        update_query["salary"] = update_data["salary"]

    # Perform update in MongoDB
    payroll_collection.update_one({"username": username}, {"$set": update_query})

    return {"message": "Payroll updated successfully"}


##################################################################################################################
#Raise Request Approval (Works)

@router.put("/hr/raise-request/approval/{raise_request_id}")
def hr_manage_raise_request(
    raise_request_id: str,
    action: str = Form(...),  # Accept or Reject
    current_user: dict = Depends(get_current_user)
):
    # Ensure HR access
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Access denied. HR only.")

    if action not in ["accept", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'accept' or 'reject'.")

    # Find the employee's payroll record that contains this raise request
    payroll = payroll_collection.find_one({"raise_requests.request_id": raise_request_id})

    if not payroll:
        raise HTTPException(status_code=404, detail="Raise request not found in any payroll record.")

    # Find the specific raise request
    raise_request = next((r for r in payroll.get("raise_requests", []) if str(r["request_id"]) == raise_request_id), None)

    if not raise_request:
        raise HTTPException(status_code=404, detail="Raise request not found.")

    # If action is accept, update salary and approve raise request
    if action == "accept":
        update_result = payroll_collection.update_one(
            {"raise_requests.request_id": raise_request_id},
            {
                "$set": {
                    "raise_requests.$.status": "approved",
                },
                "$inc": {
                    "salary": raise_request["requested_amount"]  # Increase salary by requested amount
                }
            }
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to approve raise request.")

        return {
            "message": "Raise request approved and salary updated.",
            "raise_request_id": raise_request_id
        }

    # If action is reject, only update the request status
    if action == "reject":
        update_result = payroll_collection.update_one(
            {"raise_requests.request_id": raise_request_id},
            {"$set": {"raise_requests.$.status": "rejected"}}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to reject raise request.")

        return {"message": "Raise request rejected.", "raise_request_id": raise_request_id}
    

##################################################################################################################
# Fetching Raise Requests (Works)

@router.get("/hr/raise-requests/pending")
def fetch_pending_raise_requests(current_user: dict = Depends(get_current_user)):
    # Ensure HR access
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Access denied. HR only.")

    # Find all payroll records that contain raise requests
    payrolls = payroll_collection.find({"raise_requests": {"$exists": True, "$ne": []}})

    pending_requests = []
    for payroll in payrolls:
        username = payroll.get("username")  # Get the employee's username
        for request in payroll.get("raise_requests", []):
            if request.get("status") == "pending":  # Only fetch pending requests
                pending_requests.append({
                    "username": username,
                    "request_id": request["request_id"],
                    "requested_amount": request["requested_amount"],
                    "reason": request["reason"],
                    "status": request.get("status", "pending"),
                    "requested_at": request.get("requested_at"),
                })

    if not pending_requests:
        raise HTTPException(status_code=404, detail="No pending raise requests found.")

    return {"pending_raise_requests": pending_requests}
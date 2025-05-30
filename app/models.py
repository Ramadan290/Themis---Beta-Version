from pydantic import BaseModel, root_validator
from typing import Optional, List
from bson import ObjectId
from pydantic import Field
from datetime import date, datetime
import uuid


###############################################################################################################
####################################### AUTHORIZATION ###########################################################


# User model for login/registration
class User(BaseModel):
    username: str
    password: str

# Response model for user, including alias for MongoDB's _id
class UserInDB(BaseModel):
    username: str
    role: str
    id: str = Field(..., alias="_id")  # Map MongoDB's _id to 'id'
    hashed_password: str

    class Config:
        # Convert ObjectId to string when serializing
        json_encoders = {ObjectId: str}
        from_attributes = True  # Updated for Pydantic V2


# Token model for JWT response
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


###############################################################################################################
############################################# PAYROLL ###########################################################


# Appraisal and Penalty models
class Appraisal(BaseModel):
    amount: int
    date: str  # Change this to string format (YYYY-MM-DD)

    class Config:
        # Convert date to string format during serialization
        json_encoders = {
            date: lambda v: v.isoformat()  # Use ISO 8601 format (YYYY-MM-DD)
        }
        from_attributes = True  # Updated for Pydantic V2


class Penalty(BaseModel):
    amount: float
    reason: str


# RaiseRequest model for tracking raise requests
class RaiseRequest(BaseModel):
    requested_amount: float
    reason: str
    status: str = "pending"  # Default status is "pending", options are "approved", "rejected"
    requested_at: str = datetime.utcnow().isoformat()  # Timestamp when the raise request is made
    request_id: Optional[str] = None  # Make request_id optional, it will be generated automatically

    @root_validator(pre=True)
    def generate_request_id(cls, values):
        # Automatically generate a unique request_id if not provided
        if 'request_id' not in values:
            values['request_id'] = str(uuid.uuid4())  # Generate a unique ID for each raise request
        return values

    class Config:
        from_attributes = True  # Updated for Pydantic V2


class Payroll(BaseModel):
    salary: float
    benefits: List[str]
    appraisals: List[Appraisal]
    penalties: List[Penalty]
    raise_requests: Optional[List[RaiseRequest]] = []  # Optional field to track raise requests

    class Config:
        from_attributes = True  # Updated for Pydantic V2
        json_encoders = {
            date: lambda v: v.isoformat()  # Convert date to ISO 8601 format (YYYY-MM-DD)
        }


###############################################################################################################
############################################ ATTENDANCE ##########################################################


# Sick Note model to be embedded inside Attendance
class SickNote(BaseModel):
    reason: str
    status: str = "Pending"  # Default value: Pending, options: Accepted, Rejected
    review_comments: Optional[str] = None
    file_name: Optional[str] = None  # Path to the uploaded file if provided
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


# Attendance model with embedded sick note
class Attendance(BaseModel):
    attendance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Generate unique ID
    date: date
    status: str  # Options: Present, Absent , Late 
    manual_entry: bool
    sick_note: Optional[SickNote] = None  # Embedded sick note

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()  # Convert datetime to string format
        }
        from_attributes = True  # Updated for Pydantic V2


###############################################################################################################
############################################ NEWS ##############################################################


class Comment(BaseModel):
    comment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Generate unique ID
    username: str
    content: str
    date: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))


class News(BaseModel):
    news_id: str  # Custom news ID for frontend reference
    title: str
    content: str
    date: date
    author: str
    comments: Optional[List[Comment]] = []

    class Config:
        from_attributes = True  # Updated for Pydantic V2


###############################################################################################################
############################################ STATUS ############################################################


class Status(BaseModel):
    username : str
    position : str
    department : str
    start_date : date
    status : str
    completion_rate : int
    project_contribtution : Optional[List] = []
    interaction_level :  Optional[List] = []
    workload_handling : Optional[List] = []
 



# Define a request model for HR approval
class DepartmentUpdateRequest(BaseModel):
    accept_change: bool
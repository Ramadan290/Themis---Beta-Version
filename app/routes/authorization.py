from fastapi import  Form , APIRouter, HTTPException, Depends 
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from fastapi import HTTPException, Depends, status


from app.auth import create_access_token, hash_password, verify_password, verify_token , get_current_user , create_refresh_token
from app.models import User, UserInDB, Token
from app.config import users_collection


router = APIRouter()

# OAuth2PasswordBearer is used to extract JWT token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


#################################################################################################################3

# POST register route to create a new user (Works)

@router.post("/register")
def register_user(user: User):
    # Check if the user already exists
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash the password before storing it
    hashed_password = hash_password(user.password)
    new_user = {"username": user.username, "hashed_password": hashed_password, "role": "employee"}
    
    result = users_collection.insert_one(new_user)
    return {"message": "User created successfully", "id": str(result.inserted_id)}



####################################################################################################################
# Route to Login and get JWT token (Works)

@router.post("/login", response_model=Token)
def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
):
    # Find the user in the database by username
    db_user = users_collection.find_one({"username": username})
    
    # If the user is not found or password doesn't match, raise error
    if not db_user or not verify_password(password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Generate the access token (expires in 30 minutes)
    access_token = create_access_token(data={
        "sub": username,  # Use 'sub' for the username as the unique identifier
        "role": db_user["role"],  # The user's role
    })
    
    # Generate the refresh token (expires in 7 days)
    refresh_token = create_refresh_token(data={
        "sub": username,  # Use 'sub' for the username as the unique identifier
        "role": db_user["role"],  # The user's role
    })

    # Return both the access token and the refresh token
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # Include the refresh token
        "token_type": "bearer"
    }


#######################################################################################################################
# Helper function to convert MongoDB ObjectId to string (Works)

def serialize_user(user: dict):
    user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return user

# Route to get current user's info
@router.get("/users/me", response_model=UserInDB)
def read_users_me(current_user: dict = Depends(get_current_user)):
    user = serialize_user(current_user)  # Serialize the user document
    print(f"Current user: {current_user}")
    return user


#######################################################################################################################
#Endpoint for Refreshing token (Works)

@router.post("/refresh_token", response_model=Token)
async def refresh_access_token(refresh_token: str):
    try:
        # Verify and decode the refresh token
        payload = verify_token(refresh_token)
        
        # Create a new access token using the user data from the refresh token
        user_data = {"id": payload["id"], "sub": payload["sub"]}
        new_access_token = create_access_token(data=user_data)
        
        return {"access_token": new_access_token, "token_type": "bearer"}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
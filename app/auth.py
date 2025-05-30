from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from app.config import users_collection  # MongoDB collection for users
from fastapi.security import OAuth2PasswordBearer

# Secret key to encode JWT tokens
SECRET_KEY = "THEMIS"  # Change this to a secure key 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expires in 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7


# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer is used to extract JWT token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Function to hash passwords
def hash_password(password: str):
    return pwd_context.hash(password)

# Function to verify passwords
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Function to create JWT token with employee ID and role
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify JWT token and extract user info
def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials for token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception

# Function to get current user from the JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode the token and extract the username
    payload = verify_token(token)
    
    username: str = payload.get("sub")  # 'sub' is the username in the token

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Query the user by username
    user = users_collection.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# Function to check if the user has the required role
def role_required(role: str):
    def _role_required(user: dict = Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource",
            )
        return user
    return _role_required

# Function to create refresh token
def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
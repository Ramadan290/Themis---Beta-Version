from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as api_router


app = FastAPI()

# Include API routes
app.include_router(api_router)

# Serve frontend files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ✅ Allow frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (you can restrict it later)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Redirect root to login.html
@app.get("/")
def home():
    return RedirectResponse(url="frontend/authorization/login/login.html")

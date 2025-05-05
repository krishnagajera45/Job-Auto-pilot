from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tailor import router as tailor_router
from users import router as users_router
from preferences import router as preferences_router
from automated_workflow import JobApplicationWorkflow, router as automated_workflow_router

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tailor_router)
app.include_router(users_router)
app.include_router(preferences_router)
app.include_router(automated_workflow_router)

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}


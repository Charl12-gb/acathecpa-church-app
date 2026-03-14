from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
# from sqlalchemy.orm import Session # Removed as it was only for on_startup type hinting

from app.core.config import settings
# Updated import for professor_router to get both routers
from app.routers import user_router, content_router, course_router, live_session_router, auth as auth_router
from app.routers.professor_router import router as professor_main_router, admin_dashboard_router # Import both routers
from app.routers.student_router import student_dashboard_router # Import student_dashboard_router
# Import permission routers
from app.permissions.routers import roles_router, permissions_router, role_permissions_router, user_permissions_router


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
directory = os.path.join(BASE_DIR, "../static")

if not os.path.exists(directory):
    os.makedirs(directory)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    # openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware Configuration
# Update this with the actual origin of your Vue.js frontend
origins = [
    "http://localhost:5173", # Default Vite dev server port
    "http://127.0.0.1:5173",
    "http://localhost:3000", # Common alternative for Vue dev
    "http://127.0.0.1:3000",
    # Add your production frontend URL when you have one
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
# All routers are already prefixed with settings.API_V1_STR in their respective files.
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(content_router.router)
app.include_router(course_router.router)
app.include_router(live_session_router.router)
app.include_router(professor_main_router) # Use the imported professor_main_router
app.include_router(admin_dashboard_router) # Add the new admin_dashboard_router
app.include_router(student_dashboard_router) # Add the new student_dashboard_router

# Include permission routers
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(role_permissions_router)
app.include_router(user_permissions_router)

@app.get("/", tags=["Root"]) # Added tags for better OpenAPI docs
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} - Version {settings.PROJECT_VERSION}"}
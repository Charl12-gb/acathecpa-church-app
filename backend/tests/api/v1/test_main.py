import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.config import settings # For more specific assertions

# Mark tests as asyncio for pytest-asyncio
pytestmark = pytest.mark.asyncio

async def test_read_root(client: AsyncClient): # Use the client fixture from conftest.py
    response = await client.get("/") # The root path is / as defined in main.py
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "message" in json_response
    # Check for project name and version from settings
    assert json_response["message"] == f"Welcome to {settings.PROJECT_NAME} - Version {settings.PROJECT_VERSION}"

# Example test for an auth route (requires more setup for user, etc.)
# This is commented out as it needs a test user and potentially more mocking
# or a fixture to provide an authenticated client.
# async def test_register_user(client: AsyncClient, db_session): # db_session fixture if test interacts with DB directly
#     user_data = {
#         "email": "testuser@example.com", # Unique email for test
#         "name": "Test User",
#         "password": "aSecurePassword123!" 
#     }
#     # Note: The prefix settings.API_V1_STR is already part of the router definition
#     # So if auth_router.router is included in main.py without a global prefix for all /api/v1 routes,
#     # and auth_router itself has prefix="/api/v1/auth", then the path is correct.
#     # If main.py includes auth_router with prefix="/api/v1", then the path here would be "/auth/register"
#     # Based on current setup, auth_router is included directly, and its prefix is /api/v1/auth
#     response = await client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
#     
#     # Depending on how your DB is cleaned up (or if test users persist),
#     # this might fail on subsequent runs if the user isn't deleted.
#     # The db_session fixture with rollback helps here for direct DB changes,
#     # but API calls commit transactions.
#     
#     if response.status_code == status.HTTP_400_BAD_REQUEST and "Email already registered" in response.text:
#         # This is acceptable if the test DB is not cleaned between full test suite runs
#         # and this test ran after one where the user was successfully created.
#         # For true idempotency, ensure clean state or use unique data.
#         print("User already registered, which might be okay depending on test DB state.")
#         pass 
#     else:
#         assert response.status_code == status.HTTP_201_CREATED # Assuming 201 for successful registration
#         json_response = response.json()
#         assert json_response["email"] == user_data["email"]
#         assert json_response["name"] == user_data["name"]
#         assert "id" in json_response
#         # Ensure password is not returned
#         assert "hashed_password" not in json_response 
#         assert "password" not in json_response
#
#         # Optionally, clean up the user from the database if not using full rollback for API tests
#         # from app.services import user_service
#         # from app.database import SessionLocal
#         # with SessionLocal() as temp_db: # Use a temporary session for cleanup
#         #     user_service.delete_user(temp_db, user_id=json_response["id"])

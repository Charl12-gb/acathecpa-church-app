import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Generator

# Assuming your project structure allows these imports
from app.models.user import User
from app.permissions.models import Roles
from app.models.professor import ProfessorProfile
from app.schemas.professor import ProfessorProfileCreate, ProfessorProfileUpdate
from app.schemas.user import UserCreate
from app.permissions.schemas import RoleBase, RoleCreate
import app.services
from app.services import user_service
from app.services.auth_service import get_password_hash
from app.permissions import services as roles_service
from app.services import professor_service

# Mock database session for tests - In a real setup, this would come from conftest.py
# For this exercise, we'll assume a 'db' fixture is provided by pytest-fastapi-sqlalchemy or similar.

# Helper function to create a role (if not handled by fixtures or initial data)
def create_test_role(db: Session, role_name: str = "professor") -> Roles:
    role = db.query(Roles).filter(Roles.name == role_name).first()
    if role:
        return role
    role_in = RoleCreate(name=role_name, description=f"Test {role_name} role")
    return roles_service.create_role(db=db, role_in=role_in)

# Helper function to create a user for testing
def create_test_user(db: Session, email: str, full_name: str = "Test User", role_name: str = "professor") -> User:
    # Ensure the role exists
    role = create_test_role(db, role_name)

    user_in = UserCreate(
        email=email,
        password=get_password_hash("testpassword"), # Use the actual hashing function
        name=full_name,
        # role_id=role.id # Assign role_id if your UserCreate schema and User model expect it directly
        # If role is assigned differently (e.g. after user creation or via a role name string), adjust here.
    )
    # This might conflict if user_service.create_user expects different parameters or handles roles differently.
    # Adapting to a generic user creation. The actual user creation might be auth_service.register_user
    # For simplicity, using a direct creation method if available, or assuming a basic user_service.create_user

    # Check if user_service.create_user exists and its signature
    # This is a placeholder, actual user creation might be more complex (e.g., using auth_service.register_user)
    # For now, let's assume a simple user creation or that user is created manually in tests.
    # This part needs to align with how users are actually created in your app's services.

    # A more direct way if auth_service is not to be used here:
    db_user = User(
        email=email,
        hashed_password=get_password_hash("testpassword"),
        name=full_name,
        is_active=True,
        role_id=role.id # This assumes User model has role_id and it's directly settable
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Tests for create_professor_profile
def test_create_professor_profile_success(db: Session):
    user = create_test_user(db, email="prof1@example.com", role_name="professor")
    profile_in = ProfessorProfileCreate(
        specialization="Quantum Physics",
        bio="Experienced quantum physicist.",
        # user_id is not in create schema, it's a path param in service
    )

    created_profile = professor_service.create_professor_profile(db=db, user_id=user.id, profile_in=profile_in)

    assert created_profile is not None
    assert created_profile.user_id == user.id
    assert created_profile.specialization == profile_in.specialization
    assert created_profile.bio == profile_in.bio
    assert created_profile.id is not None

    db_profile = db.query(ProfessorProfile).filter(ProfessorProfile.id == created_profile.id).first()
    assert db_profile is not None
    assert db_profile.specialization == profile_in.specialization

def test_create_professor_profile_non_existent_user(db: Session):
    profile_in = ProfessorProfileCreate(
        specialization="Ancient History",
        bio="Loves ancient history."
    )

    non_existent_user_id = 99999
    with pytest.raises(HTTPException) as excinfo:
        professor_service.create_professor_profile(db=db, user_id=non_existent_user_id, profile_in=profile_in)
    assert excinfo.value.status_code == 404 # Assuming service raises 404

def test_create_professor_profile_already_exists(db: Session):
    user = create_test_user(db, email="prof2@example.com", role_name="professor")
    profile_in1 = ProfessorProfileCreate(specialization="Botany", bio="Plant expert.")
    professor_service.create_professor_profile(db=db, user_id=user.id, profile_in=profile_in1)

    profile_in2 = ProfessorProfileCreate(specialization="Advanced Botany", bio="Even more expert.")
    with pytest.raises(HTTPException) as excinfo:
        professor_service.create_professor_profile(db=db, user_id=user.id, profile_in=profile_in2)
    assert excinfo.value.status_code == 409 # Assuming service raises 409

# Tests for get_professor_profile_by_user_id
def test_get_professor_profile_by_user_id_existing(db: Session):
    user = create_test_user(db, email="prof3@example.com", role_name="professor")
    profile_in = ProfessorProfileCreate(specialization="Marine Biology", bio="Studies marine life.")
    created_profile = professor_service.create_professor_profile(db=db, user_id=user.id, profile_in=profile_in)

    fetched_profile = professor_service.get_professor_profile_by_user_id(db=db, user_id=user.id)

    assert fetched_profile is not None
    assert fetched_profile.id == created_profile.id
    assert fetched_profile.user_id == user.id
    assert fetched_profile.specialization == profile_in.specialization

def test_get_professor_profile_by_user_id_non_existent(db: Session):
    non_existent_user_id = 99998
    fetched_profile = professor_service.get_professor_profile_by_user_id(db=db, user_id=non_existent_user_id)
    assert fetched_profile is None

# Tests for update_professor_profile
def test_update_professor_profile_success(db: Session):
    user = create_test_user(db, email="prof4@example.com", role_name="professor")
    profile_in_create = ProfessorProfileCreate(specialization="Initial Spec", bio="Initial Bio")
    created_profile = professor_service.create_professor_profile(db=db, user_id=user.id, profile_in=profile_in_create)

    profile_in_update = ProfessorProfileUpdate(
        specialization="Updated Spec",
        bio="Updated Bio",
        skills=["Python", "SQL"],
        education=[{"institution": "Test Uni", "degree": "PhD"}]
    )

    updated_profile = professor_service.update_professor_profile(db=db, user_id=user.id, profile_in=profile_in_update)

    assert updated_profile is not None
    assert updated_profile.id == created_profile.id
    assert updated_profile.specialization == profile_in_update.specialization
    assert updated_profile.bio == profile_in_update.bio
    assert updated_profile.skills == ["Python", "SQL"]
    assert updated_profile.education == [{"institution": "Test Uni", "degree": "PhD"}]

    db_profile = db.query(ProfessorProfile).filter(ProfessorProfile.id == updated_profile.id).first()
    assert db_profile is not None
    assert db_profile.specialization == "Updated Spec"
    assert db_profile.skills == ["Python", "SQL"]

def test_update_professor_profile_partial_update(db: Session):
    user = create_test_user(db, email="prof5@example.com", role_name="professor")
    profile_in_create = ProfessorProfileCreate(specialization="Astro", bio="Physics", skills=["C++"])
    created_profile = professor_service.create_professor_profile(db=db, user_id=user.id, profile_in=profile_in_create)

    profile_in_update = ProfessorProfileUpdate(bio="Astrophysics Updated") # Only update bio

    updated_profile = professor_service.update_professor_profile(db=db, user_id=user.id, profile_in=profile_in_update)

    assert updated_profile is not None
    assert updated_profile.id == created_profile.id
    assert updated_profile.specialization == "Astro" # Should remain unchanged
    assert updated_profile.bio == "Astrophysics Updated" # Should be updated
    assert updated_profile.skills == ["C++"] # Should remain unchanged

def test_update_professor_profile_non_existent(db: Session):
    non_existent_user_id = 99997
    profile_in_update = ProfessorProfileUpdate(specialization="NonExistent Update")

    updated_profile = professor_service.update_professor_profile(db=db, user_id=non_existent_user_id, profile_in=profile_in_update)
    assert updated_profile is None

# Tests for delete_professor_profile
def test_delete_professor_profile_success(db: Session):
    user = create_test_user(db, email="prof6@example.com", role_name="professor")
    profile_in_create = ProfessorProfileCreate(specialization="Genetics", bio="DNA research")
    created_profile = professor_service.create_professor_profile(db=db, user_id=user.id, profile_in=profile_in_create)

    profile_id = created_profile.id

    deleted_profile = professor_service.delete_professor_profile(db=db, user_id=user.id)

    assert deleted_profile is not None
    assert deleted_profile.id == profile_id
    assert deleted_profile.specialization == "Genetics"

    db_profile_after_delete = db.query(ProfessorProfile).filter(ProfessorProfile.id == profile_id).first()
    assert db_profile_after_delete is None

    # Assert user still exists
    db_user = db.query(User).filter(User.id == user.id).first()
    assert db_user is not None

def test_delete_professor_profile_non_existent(db: Session):
    non_existent_user_id = 99996
    deleted_profile = professor_service.delete_professor_profile(db=db, user_id=non_existent_user_id)
    assert deleted_profile is None

# Placeholder for conftest.py content usually providing 'db' fixture
# For this task, we assume 'db: Session' is correctly injected by the test runner.
# Example using in-memory SQLite for testing:
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.database import Base # Assuming your Base for models
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# @pytest.fixture()
# def db() -> Generator:
#     Base.metadata.create_all(bind=engine)
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()
#         Base.metadata.drop_all(bind=engine)

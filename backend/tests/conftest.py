import pytest
from typing import Generator, Any
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command

from app.main import app # Import your FastAPI app
from app.core.config import settings
from app.database import Base, get_db # To override get_db dependency
from app.dependencies.auth import get_current_active_user, get_current_user # For overriding auth

# Use a separate test database URL if available, otherwise use main dev DB (with caution)
# For true isolation, a separate TEST_DATABASE_URL is recommended.
# For this basic setup, we'll point to the same DB but could use transactions.
TEST_DATABASE_URL = settings.DATABASE_URL + "_test" # Convention for a test DB

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture to apply migrations before tests and clean up after
@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    # For a real test DB, you'd create it here if it doesn't exist.
    # Then run migrations.
    alembic_cfg = AlembicConfig("backend/alembic.ini") # Ensure path is correct from root
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    
    # Create all tables if they don't exist (useful if not using alembic for test db init)
    # Base.metadata.create_all(bind=engine) # Can be used if migrations are too slow for quick tests

    # Upgrade to the latest revision.
    try:
        Base.metadata.create_all(bind=engine) # Ensure tables for test DB are created before alembic stamps
        alembic_command.stamp(alembic_cfg, "head") # Stamp the DB with head if creating tables manually
    except Exception as e:
        # If create_all fails (e.g. DB doesn't exist) or stamp fails, try upgrade.
        # This is a common pattern: try to create schema directly, if not, run full migrations.
        # For a robust setup, ensure the test DB exists.
        print(f"Initial table creation/stamp failed: {e}. Attempting full upgrade.")
        try:
            alembic_command.upgrade(alembic_cfg, "head")
        except Exception as upgrade_e:
            print(f"Alembic upgrade also failed: {upgrade_e}")
            # Depending on policy, might want to raise this error or proceed with caution
            pass 
            
    yield
    # Downgrade and clean up the database after tests run
    # alembic_command.downgrade(alembic_cfg, "base")
    # Or, more simply, drop all tables (if they were created by Base.metadata.create_all)
    # Base.metadata.drop_all(bind=engine)
    # For this setup, we'll skip automatic downgrade to keep it simple. User can manually reset test DB.


# Override the get_db dependency for tests
def override_get_db() -> Generator[Session, Any, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override auth dependencies for tests where auth is not the focus
def override_get_current_user():
    # Return a mock/test user or raise not authenticated if needed by specific tests
    # For now, let's assume tests that need auth will mock this specifically or use a logged-in client
    pass # This needs to be a callable that returns a User-like object or raises

def override_get_current_active_user():
    # Similar to above
    pass


@pytest.fixture(scope="module") # Changed to module for potentially fewer app setups
def test_app() -> FastAPI:
    # Apply overrides for dependencies
    app.dependency_overrides[get_db] = override_get_db
    # To test protected endpoints, you'll need a more sophisticated way to mock auth
    # or a fixture that logs in a test user.
    # app.dependency_overrides[get_current_user] = override_get_current_user
    # app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    return app


@pytest.fixture(scope="module") # Changed to module
async def client(test_client_app: FastAPI) -> AsyncClient: # Corrected: client depends on test_client_app
    async with AsyncClient(app=test_client_app, base_url="http://test") as ac:
        yield ac

# Renamed test_app to test_client_app to avoid conflict with pytest's internal 'app' fixture if any
@pytest.fixture(scope="module")
def test_client_app() -> FastAPI:
    app.dependency_overrides[get_db] = override_get_db
    # You might want to set up a specific test user here for authenticated routes
    # For now, unauthenticated client:
    return app


# Fixture for a database session, using transactions that can be rolled back
@pytest.fixture(scope="function") # function scope for transaction rollback
def db_session() -> Generator[Session, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    # Use TestingSessionLocal that is bound to the engine for test DB
    session = TestingSessionLocal(bind=connection) 
    
    # Begin a nested transaction for the session if the dialect supports it (e.g. PostgreSQL)
    # This helps in rolling back changes made within the test function without affecting
    # the outer transaction managed by `connection.begin()`.
    # For SQLite, this might behave differently.
    # nested_transaction = session.begin_nested() # Optional: for finer control with some DBs

    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

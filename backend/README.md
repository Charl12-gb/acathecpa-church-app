# Backend (FastAPI Application)

This directory contains the FastAPI backend for the application. It provides APIs for user authentication, content management, course handling, and live sessions.

## Project Structure

-   `app/`: Main application code.
    -   `core/`: Configuration (settings).
    -   `models/`: SQLAlchemy database models.
    -   `schemas/`: Pydantic schemas for data validation and serialization.
    -   `routers/`: API endpoint definitions.
    -   `services/`: Business logic.
    -   `dependencies/`: Shared dependencies (e.g., authentication).
    -   `database.py`: Database engine and session setup.
-   `alembic/`: Alembic migration scripts and configuration.
-   `tests/`: Pytest unit and integration tests.
-   `main.py`: FastAPI application entry point.
-   `.env.example`: Example environment variables. Copy to `.env` and fill in your values.
-   `requirements.txt`: Python dependencies.
-   `alembic.ini`: Alembic configuration file.

## Setup and Running

1.  **Create a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    *   Copy `.env.example` to a new file named `.env`.
    *   Update the `.env` file with your actual database connection details (PostgreSQL), JWT secret key, etc.
    ```env
    DATABASE_URL=postgresql://your_user:your_password@your_host:5432/your_db_name
    SECRET_KEY=your_strong_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    REFRESH_TOKEN_EXPIRE_DAYS=7
    ```

4.  **Database Migrations (PostgreSQL server must be running and accessible):**
    *   The initial migration script has been generated in `alembic/versions/`.

    * Generate the initial migration script:
    ```bash
    alembic revision --autogenerate -m "initial migration"
    ```
    
    *   To apply migrations and create database tables, run:
        ```bash
        # Ensure your .env file is configured and your PostgreSQL server is running
        alembic upgrade head
        ```
    *   (Note: If you need to generate a new migration after model changes: `alembic revision -m "description_of_changes"`)


5.  **Run the FastAPI development server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The application will typically be available at `http://127.0.0.1:8000`.
    API documentation (Swagger UI) will be at `http://127.0.0.1:8000/docs`.

## Testing

1.  Ensure you have a separate test database configured (e.g., by appending `_test` to your main database name in `DATABASE_URL` for tests, or configure `TEST_DATABASE_URL` in `tests/conftest.py`).
2.  The `tests/conftest.py` attempts to run migrations on the test database.
3.  Run tests using pytest:
    ```bash
    pytest
    ```

# Seeder uniquement les rôles et permissions
python manage.py seed-roles-permissions

# Seeder uniquement l'utilisateur admin
python manage.py seed-default-user

# Seeder tout d'un coup
python manage.py seed-all

# Voir l'aide
python manage.py --help
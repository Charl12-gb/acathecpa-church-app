from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from fastapi import HTTPException, status
from app.permissions.models import Permissions, RolesPermissions, Roles
from app.schemas.user import UserCreate, ProfessorUserAndProfileCreate
from app.core.config import settings
from app.models.professor import ProfessorProfile as ProfessorProfileModel
from app.permissions.models import UserRoleEnum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"} # Add a type claim
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    return db.query(User).filter(User.phone == phone).first()

def get_role_by_name(db: Session, role_name: str) -> Optional[Roles]:
    return db.query(Roles).filter(Roles.name == role_name).first()

def create_professor_user_and_profile(db: Session, *, payload: ProfessorUserAndProfileCreate) -> User:
    # 1. Vérifier si l'email utilisateur existe déjà
    existing_user = get_user_by_email(db, email=payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà.",
        )

    professor_role_name_identifier = UserRoleEnum.professor
    role = get_role_by_name(db, role_name=professor_role_name_identifier)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Le rôle '{professor_role_name_identifier}' n'a pas été trouvé dans la base de données."
        )

    # ✅ Définir les champs utilisateurs et profil
    user_fields = User.__table__.columns.keys()
    profile_fields = ProfessorProfileModel.__table__.columns.keys()

    user_data_dict = {}
    profile_data_dict = {}

    payload_dict = payload.model_dump()

    for key, value in payload_dict.items():
        if key in user_fields and key not in ['id', 'hashed_password', 'role_id', 'professor_profile', 'created_at', 'updated_at']:
            user_data_dict[key] = value
        elif key in profile_fields and key not in ['id', 'user_id']:
            if key in ["social_links", "education", "experience", "skills"]:
                profile_data_dict[key] = value
            else:
                profile_data_dict[key] = value

    # 4. Créer l'objet User
    hashed_password = get_password_hash(payload.password)
    db_user = User(
        **user_data_dict,
        hashed_password=hashed_password,
        role_id=role.id,
    )
    db_profile = ProfessorProfileModel(**profile_data_dict)
    db_user.professor_profile = db_profile

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_with_profile(db: Session, user_id: int) -> Optional[User]:
    return (
        db.query(User)
        .options(joinedload(User.professor_profile), joinedload(User.role))
        .filter(User.id == user_id)
        .first()
    )


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    user_role_id = user.role
    if user.role:
        user_role_id = db.query(Roles).filter(Roles.name ==  user.role).first()
    else:
        raise ValueError("Role must be specified or defaulted to " + user.role)
    
    user_role_id = user_role_id.id if user_role_id else None
    if not user_role_id:
        raise ValueError("Invalid role specified or role does not exist in the database.")
    
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        phone=user.phone,
        country=user.country,
        birthdate=user.birthdate,
        role_id=user_role_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def generate_password_reset_token(email: str) -> str:
    """
    Generates a JWT token for password reset.
    Token expires in 15 minutes.
    """
    expire = datetime.utcnow() + timedelta(minutes=15) 
    to_encode = {"exp": expire, "sub": email, "type": "password_reset"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verifies the password reset token.
    Returns the email if the token is valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            return None # Not a password reset token

        email: Optional[str] = payload.get("sub")
        return email
    except JWTError: 
        return None

def update_password(db: Session, email: str, new_password: str) -> bool:
    """
    Updates the password for a user identified by email.
    Returns True if successful, False otherwise.
    """
    user = get_user_by_email(db, email=email)
    if user:
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return True
    return False

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks # Added BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt, JWTError
from pydantic import BaseModel, validator, EmailStr # Added EmailStr
import re
from typing import Optional

from app.schemas import user as user_schema, token as token_schema
from app.services import auth_service
from app.dependencies import auth as auth_deps
from app.core.config import settings
from app.permissions.dependencies import RequirePermission
from app.services.email_service import send_email # Added for sending welcome email
import logging # Added for logging email errors

# Configure logging
logger = logging.getLogger(__name__)

# Pydantic models for forgot/reset password
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

router = APIRouter(prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])

# Modèle personnalisé pour le login flexible
class FlexibleLoginRequest(BaseModel):
    username: str  # Peut être email ou téléphone
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not v:
            raise ValueError('Username is required')
        
        # Vérifier si c'est un email ou un téléphone
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_pattern = r'^\+?[1-9]\d{1,14}$'  # Format E164 simplifié
        
        if not (re.match(email_pattern, v) or re.match(phone_pattern, v)):
            raise ValueError('Username must be a valid email or phone number')
        
        return v

# Service d'authentification étendu
class ExtendedAuthService:
    @staticmethod
    def authenticate_user_flexible(db: Session, username: str, password: str):
        """
        Authentifie un utilisateur avec email ou téléphone
        """
        # Déterminer si c'est un email ou un téléphone
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, username):
            # C'est un email
            user = auth_service.get_user_by_email(db, email=username)
        else:
            # C'est un téléphone
            user = auth_service.get_user_by_phone(db, phone=username)
        
        if not user:
            return None
        
        # Vérifier le mot de passe
        if not auth_service.verify_password(password, user.hashed_password):
            return None
        
        return user

# Routes d'authentification
@router.post("/register", response_model=user_schema.User)
async def register_user( # Changed to async def
    user_in: user_schema.UserCreate, 
    db: Session = Depends(auth_deps.get_db),
):
    """
    Créer un nouvel utilisateur avec email et/ou téléphone
    """
    # Vérifier si l'email existe déjà
    if user_in.email:
        db_user = auth_service.get_user_by_email(db, email=user_in.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Vérifier si le téléphone existe déjà
    if user_in.phone:
        db_user = auth_service.get_user_by_phone(db, phone=user_in.phone)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered",
            )
    
    new_user = auth_service.create_user(db=db, user=user_in)

    if new_user and new_user.email: # Check if user was created and has an email
        try:
            subject = f"Welcome to {settings.PROJECT_NAME}!"
            # Use a more descriptive name if available, otherwise fallback to splitting email
            user_name = new_user.name if new_user.name else new_user.email.split('@')[0]
            body = f"""Hi {user_name},

                Welcome to {settings.PROJECT_NAME}! We're glad to have you.

                Thanks,
                The {settings.PROJECT_NAME} Team"""
            # Using subtype "plain" for now. HTML would be: subtype="html", body="<html>...</html>"
            await send_email(subject=subject, recipient=new_user.email, body=body, subtype="plain")
            logger.info(f"Welcome email sent to {new_user.email}")
        except Exception as e:
            logger.error(f"Error sending welcome email to {new_user.email}: {e}")
            # Do not fail registration if email sending fails. Log and continue.

    return new_user

@router.post("/login", response_model=token_schema.Token)
def login_for_access_token(
    db: Session = Depends(auth_deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Connexion avec email ou téléphone et mot de passe
    """
    user = ExtendedAuthService.authenticate_user_flexible(
        db, username=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        subject=user.email or user.phone, 
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = auth_service.create_refresh_token(
        subject=user.email or user.phone, 
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login/flexible", response_model=token_schema.Token)
def login_flexible(
    login_request: FlexibleLoginRequest,
    db: Session = Depends(auth_deps.get_db)
):
    """
    Connexion alternative avec validation personnalisée
    """
    user = ExtendedAuthService.authenticate_user_flexible(
        db, username=login_request.username, password=login_request.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Account is inactive"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        subject=user.email or user.phone, 
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = auth_service.create_refresh_token(
        subject=user.email or user.phone, 
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/token/refresh", response_model=token_schema.Token)
def refresh_access_token(
    db: Session = Depends(auth_deps.get_db),
    refresh_token_str: str = Depends(auth_deps.oauth2_scheme)
):
    """
    Rafraîchir le token d'accès
    """
    try:
        payload = jwt.decode(
            refresh_token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token type"
            )
        
        subject: str = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token: no subject"
            )
        
        # Chercher l'utilisateur par email ou téléphone
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, subject):
            user = auth_service.get_user_by_email(db, email=subject)
        else:
            user = auth_service.get_user_by_phone(db, phone=subject)
        
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User not found or inactive"
            )

        new_access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = auth_service.create_access_token(
            subject=user.email or user.phone, 
            expires_delta=new_access_token_expires
        )
        
        new_refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = auth_service.create_refresh_token(
            subject=user.email or user.phone, 
            expires_delta=new_refresh_token_expires
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": user
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(auth_deps.get_db)
):
    """
    Send a password reset email to the user.
    """
    user = auth_service.get_user_by_email(db, email=payload.email)
    if user and user.is_active:
        try:
            password_reset_token = auth_service.generate_password_reset_token(email=user.email)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={password_reset_token}"

            subject = f"Reset Your Password for {settings.PROJECT_NAME}"
            body = f"""Hi {user.name or user.email.split('@')[0]},

                Someone requested a password reset for your account on {settings.PROJECT_NAME}.
                If this was you, please click the link below to reset your password:
                {reset_url}

                If you did not request this, please ignore this email. This link will expire in 15 minutes.

                Thanks,
                The {settings.PROJECT_NAME} Team"""

            background_tasks.add_task(send_email, subject=subject, recipient=user.email, body=body, subtype="plain")
            logger.info(f"Password reset email queued for {user.email}")
        except Exception as e:
            # Log the error, but still return a generic message to the client
            logger.error(f"Error during forgot password process for {payload.email}: {e}")
    else:
        # Log if user not found or inactive, but don't reveal this to client
        logger.info(f"Password reset request for non-existent or inactive user: {payload.email}")

    # Always return a generic success message to prevent user enumeration
    return {"message": "If an account with that email exists, a password reset link has been sent."}

@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(auth_deps.get_db)
):
    """
    Reset user's password using a valid token.
    """
    email = auth_service.verify_password_reset_token(token=payload.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token. Please request a new password reset."
        )

    user = auth_service.get_user_by_email(db, email=email) # Re-fetch user to ensure still valid
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or inactive. Cannot reset password."
        )

    success = auth_service.update_password(db=db, email=email, new_password=payload.new_password)
    if success:
        # Optionally, send a confirmation email that password was changed
        try:
            subject = f"Your Password for {settings.PROJECT_NAME} Has Been Changed"
            body = f"""Hi {user.name or user.email.split('@')[0]},

                This is a confirmation that the password for your account on {settings.PROJECT_NAME} has just been changed.

                If you did not authorize this change, please contact support immediately.

                Thanks,
                The {settings.PROJECT_NAME} Team"""
            # This can also be a background task if preferred
            await send_email(subject=subject, recipient=user.email, body=body, subtype="plain")
            logger.info(f"Password changed confirmation email sent to {user.email}")
        except Exception as e:
            logger.error(f"Error sending password change confirmation to {user.email}: {e}")

        return {"message": "Password updated successfully. You can now log in with your new password."}
    else:
        # This case should ideally be rare if token verification and user check passed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # Or 400 if user somehow became invalid
            detail="Could not reset password due to an unexpected error."
        )

@router.get("/users/me", response_model=user_schema.User)
def read_users_me(
    current_user: user_schema.User = Depends(RequirePermission("view_own_profile"))
):
    """
    Obtenir les informations de l'utilisateur actuel
    """
    return current_user

@router.get("/validate-username/{username}")
def validate_username(username: str):
    """
    Valider si un nom d'utilisateur est un email ou téléphone valide
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    phone_pattern = r'^\+?[1-9]\d{1,14}$'
    
    is_email = bool(re.match(email_pattern, username))
    is_phone = bool(re.match(phone_pattern, username))
    
    if not (is_email or is_phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be a valid email or phone number"
        )
    
    return {
        "username": username,
        "type": "email" if is_email else "phone",
        "valid": True
    }

# Route pour changer de méthode de connexion
@router.post("/link-account")
def link_account(
    email_or_phone: str,
    current_user: user_schema.User = Depends(RequirePermission("manage_own_account"))
):
    """
    Lier un email ou téléphone à un compte existant
    """
    # Cette route permettrait d'ajouter un email à un compte qui n'a qu'un téléphone
    # ou vice versa
    pass
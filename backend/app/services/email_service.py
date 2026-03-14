import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

def get_mail_config():
    """Create mail configuration only when needed and validate settings."""
    required_fields = [
        settings.MAIL_USERNAME,
        settings.MAIL_PASSWORD, 
        settings.MAIL_FROM,
        settings.MAIL_SERVER
    ]
    
    if not all(required_fields):
        missing_fields = []
        if not settings.MAIL_USERNAME:
            missing_fields.append("MAIL_USERNAME")
        if not settings.MAIL_PASSWORD:
            missing_fields.append("MAIL_PASSWORD")
        if not settings.MAIL_FROM:
            missing_fields.append("MAIL_FROM")
        if not settings.MAIL_SERVER:
            missing_fields.append("MAIL_SERVER")
            
        logger.error(f"Missing required email configuration: {', '.join(missing_fields)}")
        return None
    
    try:
        return ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS,
            TEMPLATE_FOLDER=None,  # No templates for now
        )
    except Exception as e:
        logger.error(f"Failed to create mail configuration: {e}")
        return None

async def send_email(subject: str, recipient: str, body: str, subtype: str = "html"):
    """Send email with proper error handling."""
    
    if not settings.MAIL_ENABLED:
        logger.info("Email sending is disabled. Skipping sending email.")
        return {"status": "disabled", "message": "Email sending is disabled"}

    # Get mail configuration
    conf = get_mail_config()
    if conf is None:
        error_msg = "Email configuration is incomplete or invalid"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    # Validate recipient
    if not recipient or not recipient.strip():
        error_msg = "Recipient email is required"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    try:
        message = MessageSchema(
            subject=subject,
            recipients=[recipient],  # Must be a list
            body=body,
            subtype=subtype,
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Email sent successfully to {recipient} with subject: {subject}")
        return {"status": "success", "message": f"Email sent to {recipient}"}
        
    except Exception as e:
        error_msg = f"Error sending email to {recipient}: {str(e)}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

async def send_welcome_email(user_email: str, user_name: str = None):
    """Send welcome email to new user."""
    name_part = f" {user_name}" if user_name else ""
    subject = "Bienvenue sur ACATHECPA"
    
    body = f"""
    <html>
        <body>
            <h2>Bienvenue{name_part} !</h2>
            <p>Merci de vous être inscrit(e) sur ACATHECPA.</p>
            <p>Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter et commencer à utiliser notre plateforme.</p>
            <br>
            <p>Cordialement,</p>
            <p>L'équipe ACATHECPA</p>
        </body>
    </html>
    """
    
    return await send_email(subject, user_email, body)

async def send_password_reset_email(user_email: str, reset_token: str):
    """Send password reset email."""
    subject = "Réinitialisation de votre mot de passe - ACATHECPA"
    
    # You might want to make this URL configurable
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    body = f"""
    <html>
        <body>
            <h2>Réinitialisation de mot de passe</h2>
            <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
            <p>Cliquez sur le lien ci-dessous pour créer un nouveau mot de passe :</p>
            <p><a href="{reset_url}">Réinitialiser mon mot de passe</a></p>
            <p>Ce lien expirera dans 24 heures.</p>
            <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
            <br>
            <p>Cordialement,</p>
            <p>L'équipe ACATHECPA</p>
        </body>
    </html>
    """
    
    return await send_email(subject, user_email, body)
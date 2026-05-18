import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY
def send_verification_email(email: str, token: str) -> None:
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    params: resend.Emails.SendParams = {
        "from": settings.MAIL_FROM,
        "to": [email],
        "subject": "Verify your Isle Be There account",
        "html": f"""
            <h2>Welcome to Isle Be There!</h2>
            <p>Click the link below to verify your email address:</p>
            <a href="{verification_url}">Verify Email</a>
            <p>This link expires in 24 hours.</p>
        """,
    }
    
    resend.Emails.send(params)
    
def send_password_reset_email(email: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    params: resend.Emails.SendParams = {
        "from": settings.MAIL_FROM,
        "to": [email],
        "subject": "Reset your Isle Be There password",
        "html": f"""
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_url}">Reset Password</a>
            <p>This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
        """,
    }
    
    resend.Emails.send(params)

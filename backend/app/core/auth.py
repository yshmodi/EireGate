import os
from functools import wraps
from typing import Optional

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

"""
Supabase Client
"""

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    logger.warning("⚠️ Supabase credentials not set. Auth will not work")
    supabase: Optional[Client] = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    logger.info("✅ Supabase client initialized")

"""
Models
"""

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class SignInRequest(BaseModel):
    email: str
    password: str

"""
JWT Token Validation
"""

security = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Validate JWT token and return user data.
    Use as dependency: current_user = Depends(get_current_user)
    """
    if not supabase:
        raise HTTPException(503, "Auth service unavailable")

    token = credentials.credentials

    try:
        #Verify token with Supabase
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(401, "Invalid or expired token")

        user = user_response.user
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.user_metadata.get("full_name", ""),
            "avatar_url": user.user_metadata.get("avatar_url", "")
        }
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(401, "Invali or expired token")

async def get_optional_user(
        request: Request
) -> Optional[dict]:
    """
    Get user if token provided, None otherwise.
    Use for endpoints that work with or without auth.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]

    try:
        user_response = supabase.auth.get_user(token)
        if user_response and user_response.user:
            user = user_response.user
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.user_metadata.get("full_name", ""),
                "avatar_url": user.user_metadata.get("avatar_url", ""),
            }
    except:
        pass
    return None

"""
Auth Functions
"""

def sign_up(email: str, password: str, full_name: str = "") -> AuthResponse:
    """Register a new user with email/password."""
    if not supabase:
        raise HTTPException(503, "Auth Service Unavailable")
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })

        if response.user is None:
            raise HTTPException(400, "Registration failed")

        return AuthResponse(
            access_token=response.session.access_token if response.session else "",
            refresh_token=response.session.refresh_token if response.session else "",
            user=UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=full_name,
            )
        )
    except Exception as e:
        logger.error(f"Sign up failed {e}")
        raise HTTPException(400, str(e))

def sign_in(email: str, password: str) -> AuthResponse:
    """Sign in with email/passoword."""
    if not supabase:
        raise HTTPException(504, "Auth Service Unavailable")

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.user is None or response.session is None:
            raise HTTPException(401, "Invalid credentials")

        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user=UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name", ""),
                avatar_url=response.user.user_metadata.get("avatar_url", "")
            )
        )
    except Exception as e:
        logger.error(f"Sign in failed: {e}")
        raise HTTPException(401, "Invalid Credentails")

def sign_out(token: str) -> bool:
    """Sign out user (invalidate token)"""
    if not supabase:
        raise HTTPException(503, "Auth Service Unavailable")

    try:
        supabase.auth.sign_out()
        return True
    except Exception as e:
        logger.error(f"Sign out failed: {e}")
        return False

def get_oauth_url(provider: str, redirect_to: str = None) -> str:
    """
    Get OAuth URL for Google/Github login
    Frontend redirects user to this URL.
    """
    if not supabase:
        raise HTTPException(503, "Auth service unavailable")

    if provider not in ["google", "github"]:
        raise HTTPException(400, "Invalid provider. User 'google' or 'github'")

    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": provider,
            "options": {
                "redirect_to": redirect_to
            } if redirect_to else {}
        })
        return response.url
    except Exception as e:
        logger.error(f"OAuth URL generation failed: {e}")
        raise HTTPException(500, "Failed to generate OAuth URL")

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from ...core.auth import (
    sign_up, sign_in, sign_out, get_oauth_url,
    get_current_user, SignUpRequest, SignInRequest, AuthResponse, UserResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=AuthResponse)
async def register(request: SignUpRequest):
    """Register a new user with email/password."""
    return sign_up(request.email, request.password, request.full_name or "")

@router.post("/login", response_model=AuthResponse)
async def login(request: SignInRequest):
    """Sign in with email and password."""
    return sign_in(request.email, request.password)

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Sign out current user."""
    sign_out("")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(**current_user)

@router.get("/oauth/{provider}")
async def oauth_login(
    provider: str,
    redirect_to: Optional[str] = Query(None, description="URL to redirect after OAyuth")
):
    """
    Get OAuth URL for Google/Github login.
    1. Frontend calls to this endpoint
    2. Frontend redirects user to the returned URL
    3. User logs in with Google/Github
    4. Supabase redirects back to your app with tokens
    """
    url = get_oauth_url(provider, redirect_to)
    return{"url": url, "provider": provider}

"""Authentication endpoints"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)
from datetime import timedelta

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    role: str


class UserResponse(BaseModel):
    """User response model"""
    username: str
    role: str


# Mock user database (replace with DB in production)
MOCK_USERS = {
    "demo": {
        "password": get_password_hash("demo123"),
        "role": "OFFICER",
        "email": "demo@trinetra.ai"
    },
    "admin": {
        "password": get_password_hash("admin123"),
        "role": "ADMIN",
        "email": "admin@trinetra.ai"
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """User login - returns JWT token"""
    
    # Check if user exists
    if credentials.username not in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = MOCK_USERS[credentials.username]
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": credentials.username, "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "username": current_user["username"],
        "role": current_user["role"]
    }

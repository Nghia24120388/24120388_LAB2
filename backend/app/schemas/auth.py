from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response schema"""
    uid: str
    email: str
    display_name: Optional[str] = None
    email_verified: bool = False
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Token response schema"""
    token: str
    user: UserResponse

class UserCreate(BaseModel):
    """User creation schema"""
    uid: str
    email: EmailStr
    display_name: Optional[str] = None

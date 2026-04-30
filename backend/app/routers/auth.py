from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.dependencies.auth import get_current_user, get_optional_user
from app.schemas.auth import UserResponse, TokenResponse
from app.services.firebase_service import FirebaseService

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(user_data: Dict[str, Any]):
    """
    Login endpoint - expects Firebase ID token in request body
    """
    try:
        # Extract token from request
        token = user_data.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is required"
            )
        
        # Verify token and get user data
        from app.core.firebase_config import verify_firebase_token
        decoded_token = verify_firebase_token(token)
        
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        display_name = decoded_token.get('displayName')
        
        if not uid or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data in token"
            )
        
        # Create user in Firebase if not exists
        user_exists = FirebaseService.get_user(uid)
        if not user_exists:
            FirebaseService.create_user(uid, email, display_name)
        
        # Return token and user info
        user_response = UserResponse(
            uid=uid,
            email=email,
            display_name=display_name,
            email_verified=decoded_token.get('emailVerified', False)
        )
        
        return TokenResponse(token=token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user information
    """
    try:
        uid = current_user.get('uid')
        user_data = FirebaseService.get_user(uid)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            uid=uid,
            email=current_user.get('email'),
            display_name=current_user.get('displayName'),
            email_verified=current_user.get('emailVerified', False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.get("/check")
async def check_auth(current_user: Dict[str, Any] = Depends(get_optional_user)):
    """
    Check if user is authenticated
    """
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "uid": current_user.get('uid'),
                "email": current_user.get('email'),
                "displayName": current_user.get('displayName')
            }
        }
    else:
        return {
            "authenticated": False,
            "user": None
        }

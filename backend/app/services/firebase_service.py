from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from app.core.firebase_config import (
    create_user_in_firebase,
    get_user_data,
    save_user_place,
    get_user_places,
    delete_user_place,
    update_user_place
)

class FirebaseService:
    """Service for handling Firebase operations"""
    
    @staticmethod
    def create_user(uid: str, email: str, display_name: Optional[str] = None) -> bool:
        """Create a new user in Firebase"""
        return create_user_in_firebase(uid, email, display_name)
    
    @staticmethod
    def get_user(uid: str) -> Optional[Dict[str, Any]]:
        """Get user data from Firebase"""
        return get_user_data(uid)
    
    @staticmethod
    def save_place(uid: str, place_data: Dict[str, Any]) -> str:
        """Save a place for a user"""
        place_id = str(uuid.uuid4())
        success = save_user_place(uid, place_id, place_data)
        if success:
            return place_id
        raise Exception("Failed to save place")
    
    @staticmethod
    def get_places(uid: str) -> Dict[str, Any]:
        """Get all saved places for a user"""
        return get_user_places(uid) or {}
    
    @staticmethod
    def delete_place(uid: str, place_id: str) -> bool:
        """Delete a saved place"""
        return delete_user_place(uid, place_id)
    
    @staticmethod
    def update_place(uid: str, place_id: str, place_data: Dict[str, Any]) -> bool:
        """Update a saved place"""
        return update_user_place(uid, place_id, place_data)

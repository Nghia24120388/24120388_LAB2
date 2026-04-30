import os
import json
import firebase_admin
from firebase_admin import credentials, auth, db
from datetime import datetime
from typing import Optional, Dict, Any

# Global variables
firebase_app = None
database_url = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global firebase_app, database_url
    
    try:
        # Check if Firebase is already initialized
        if firebase_app:
            return
        
        # Get Firebase credentials from environment variables
        firebase_config_json = os.getenv("FIREBASE_CONFIG")
        database_url = os.getenv("FIREBASE_DATABASE_URL")
        
        if not firebase_config_json or not database_url:
            print("Warning: Firebase configuration not found in environment variables")
            return
        
        # Parse Firebase configuration
        firebase_config = json.loads(firebase_config_json)
        
        # Create credentials
        cred = credentials.Certificate(firebase_config)
        
        # Initialize Firebase app
        firebase_app = firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        
        print("Firebase initialized successfully")
        
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise

def get_firebase_app():
    """Get the initialized Firebase app instance"""
    return firebase_app

def verify_firebase_token(id_token: str) -> Optional[Dict[str, Any]]:
    """Verify Firebase ID token and return user data"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return None

def create_user_in_firebase(uid: str, email: str, display_name: Optional[str] = None) -> bool:
    """Create user record in Firebase Realtime Database"""
    try:
        ref = db.reference(f'users/{uid}')
        user_data = {
            'email': email,
            'displayName': display_name or email.split('@')[0],
            'createdAt': datetime.utcnow().isoformat(),
            'savedPlaces': {}
        }
        ref.set(user_data)
        return True
    except Exception as e:
        print(f"Error creating user in Firebase: {e}")
        return False

def get_user_data(uid: str) -> Optional[Dict[str, Any]]:
    """Get user data from Firebase Realtime Database"""
    try:
        ref = db.reference(f'users/{uid}')
        user_data = ref.get()
        return user_data
    except Exception as e:
        print(f"Error getting user data from Firebase: {e}")
        return None

def save_user_place(uid: str, place_id: str, place_data: Dict[str, Any]) -> bool:
    """Save a place for a user"""
    try:
        ref = db.reference(f'users/{uid}/savedPlaces/{place_id}')
        place_data['savedAt'] = datetime.utcnow().isoformat()
        ref.set(place_data)
        return True
    except Exception as e:
        print(f"Error saving user place: {e}")
        return False

def get_user_places(uid: str) -> Optional[Dict[str, Any]]:
    """Get all saved places for a user"""
    try:
        ref = db.reference(f'users/{uid}/savedPlaces')
        places = ref.get()
        return places or {}
    except Exception as e:
        print(f"Error getting user places: {e}")
        return None

def delete_user_place(uid: str, place_id: str) -> bool:
    """Delete a saved place for a user"""
    try:
        ref = db.reference(f'users/{uid}/savedPlaces/{place_id}')
        ref.delete()
        return True
    except Exception as e:
        print(f"Error deleting user place: {e}")
        return False

def update_user_place(uid: str, place_id: str, place_data: Dict[str, Any]) -> bool:
    """Update a saved place for a user"""
    try:
        ref = db.reference(f'users/{uid}/savedPlaces/{place_id}')
        place_data['updatedAt'] = datetime.utcnow().isoformat()
        ref.update(place_data)
        return True
    except Exception as e:
        print(f"Error updating user place: {e}")
        return False

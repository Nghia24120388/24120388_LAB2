from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any

from app.dependencies.auth import get_current_user
from app.schemas.poi import POIRequest, POIResult, PlaceCreate, PlaceUpdate, PlaceResponse
from app.services.overpass_service import OverpassService
from app.services.firebase_service import FirebaseService

router = APIRouter()

@router.post("/nearby", response_model=List[POIResult])
async def get_nearby_pois(request: POIRequest):
    """
    Get nearby POIs using Overpass API
    """
    try:
        results = await OverpassService.get_nearby_pois(
            request.lat, request.lon, request.radius, request.poi_types
        )
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get nearby POIs: {str(e)}"
        )

@router.get("/nearby")
async def get_nearby_pois_get(
    lat: float, lon: float, radius: int = 1000, 
    poi_types: str = None
):
    """
    Get nearby POIs using Overpass API (GET method)
    """
    try:
        poi_types_list = None
        if poi_types:
            poi_types_list = [type.strip() for type in poi_types.split(',')]
        
        results = await OverpassService.get_nearby_pois(
            lat, lon, radius, poi_types_list
        )
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get nearby POIs: {str(e)}"
        )

@router.get("/type/{poi_type}")
async def get_pois_by_type(
    poi_type: str, lat: float, lon: float, radius: int = 1000
):
    """
    Get POIs by specific type using Overpass API
    """
    try:
        results = await OverpassService.get_pois_by_type(
            poi_type, lat, lon, radius
        )
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get POIs by type: {str(e)}"
        )

# CRUD operations for saved places
@router.post("/places", response_model=PlaceResponse)
async def create_place(
    place: PlaceCreate, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Save a new place for the current user
    """
    try:
        uid = current_user.get('uid')
        
        place_data = {
            'name': place.name,
            'lat': place.lat,
            'lon': place.lon,
            'description': place.description,
            'category': place.category,
            'address': place.address,
            'tags': place.tags
        }
        
        place_id = FirebaseService.save_place(uid, place_data)
        
        return PlaceResponse(
            id=place_id,
            **place_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save place: {str(e)}"
        )

@router.get("/places", response_model=List[PlaceResponse])
async def get_user_places(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all saved places for the current user
    """
    try:
        uid = current_user.get('uid')
        places = FirebaseService.get_places(uid)
        
        place_responses = []
        for place_id, place_data in places.items():
            place_response = PlaceResponse(
                id=place_id,
                **place_data
            )
            place_responses.append(place_response)
        
        return place_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user places: {str(e)}"
        )

@router.put("/places/{place_id}", response_model=PlaceResponse)
async def update_place(
    place_id: str,
    place_update: PlaceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update a saved place
    """
    try:
        uid = current_user.get('uid')
        
        # Check if place exists
        user_places = FirebaseService.get_places(uid)
        if place_id not in user_places:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        # Prepare update data
        update_data = place_update.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update place
        success = FirebaseService.update_place(uid, place_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update place"
            )
        
        # Get updated place data
        updated_places = FirebaseService.get_places(uid)
        updated_place_data = updated_places[place_id]
        
        return PlaceResponse(
            id=place_id,
            **updated_place_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update place: {str(e)}"
        )

@router.delete("/places/{place_id}")
async def delete_place(
    place_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a saved place
    """
    try:
        uid = current_user.get('uid')
        
        # Check if place exists
        user_places = FirebaseService.get_places(uid)
        if place_id not in user_places:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        # Delete place
        success = FirebaseService.delete_place(uid, place_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete place"
            )
        
        return {"message": "Place deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete place: {str(e)}"
        )

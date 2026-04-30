from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas.map import (
    SearchRequest, SearchResult, ReverseGeocodeRequest, ReverseGeocodeResult,
    RouteRequest, RouteResult, NearestRoadRequest, NearestRoadResult
)
from app.services.nominatim_service import NominatimService
from app.services.osrm_service import OSRMService

router = APIRouter()

@router.get("/search", response_model=List[SearchResult])
async def search_places(query: str, limit: int = 10):
    """
    Search for places using Nominatim API
    """
    try:
        if not query or len(query.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query is required"
            )
        
        results = await NominatimService.search_places(query.strip(), limit)
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.post("/search", response_model=List[SearchResult])
async def search_places_post(search_request: SearchRequest):
    """
    Search for places using Nominatim API (POST method)
    """
    try:
        results = await NominatimService.search_places(
            search_request.query, 
            search_request.limit
        )
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.post("/reverse", response_model=ReverseGeocodeResult)
async def reverse_geocode(request: ReverseGeocodeRequest):
    """
    Get address from coordinates using Nominatim API
    """
    try:
        result = await NominatimService.reverse_geocode(request.lat, request.lon)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No address found for the given coordinates"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reverse geocoding failed: {str(e)}"
        )

@router.post("/route", response_model=RouteResult)
async def get_route(request: RouteRequest):
    """
    Get route between two points using OSRM API
    """
    try:
        result = await OSRMService.get_route(
            request.start_lat, request.start_lon,
            request.end_lat, request.end_lon,
            request.profile
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No route found between the given points"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route calculation failed: {str(e)}"
        )

@router.post("/nearest", response_model=NearestRoadResult)
async def get_nearest_road(request: NearestRoadRequest):
    """
    Find nearest road to a point using OSRM API
    """
    try:
        result = await OSRMService.get_nearest_road(
            request.lat, request.lon, request.profile
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No road found near the given coordinates"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Finding nearest road failed: {str(e)}"
        )

@router.get("/alternatives")
async def get_alternative_routes(
    start_lat: float, start_lon: float,
    end_lat: float, end_lon: float,
    profile: str = "driving",
    alternatives: int = 3
):
    """
    Get multiple alternative routes using OSRM API
    """
    try:
        results = await OSRMService.get_alternative_routes(
            start_lat, start_lon, end_lat, end_lon,
            profile, alternatives
        )
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No routes found between the given points"
            )
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Getting alternative routes failed: {str(e)}"
        )

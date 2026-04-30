from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SearchRequest(BaseModel):
    """Search request schema"""
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=50)

class SearchResult(BaseModel):
    """Search result schema"""
    place_id: Optional[str] = None
    display_name: str
    lat: float
    lon: float
    type: Optional[str] = None
    importance: Optional[float] = None
    address: Dict[str, Any] = {}
    bbox: List[float] = []

class ReverseGeocodeRequest(BaseModel):
    """Reverse geocode request schema"""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)

class ReverseGeocodeResult(BaseModel):
    """Reverse geocode result schema"""
    place_id: Optional[str] = None
    display_name: str
    lat: float
    lon: float
    type: Optional[str] = None
    address: Dict[str, Any] = {}

class RouteRequest(BaseModel):
    """Route request schema"""
    start_lat: float = Field(..., ge=-90, le=90)
    start_lon: float = Field(..., ge=-180, le=180)
    end_lat: float = Field(..., ge=-90, le=90)
    end_lon: float = Field(..., ge=-180, le=180)
    profile: str = Field(default="driving", pattern="^(driving|walking|cycling)$")

class RouteStep(BaseModel):
    """Route step schema"""
    distance: float
    duration: float
    geometry: Dict[str, Any]
    maneuver: Dict[str, Any]
    name: str
    mode: str

class RouteLeg(BaseModel):
    """Route leg schema"""
    distance: float
    duration: float
    summary: str
    steps: List[RouteStep]

class RouteResult(BaseModel):
    """Route result schema"""
    distance: float
    duration: float
    geometry: Dict[str, Any]
    legs: List[RouteLeg]
    weight: float
    weight_name: str

class NearestRoadRequest(BaseModel):
    """Nearest road request schema"""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    profile: str = Field(default="driving", pattern="^(driving|walking|cycling)$")

class NearestRoadResult(BaseModel):
    """Nearest road result schema"""
    location: List[float]
    name: str
    distance: float

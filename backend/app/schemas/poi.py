from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class POIRequest(BaseModel):
    """POI search request schema"""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius: int = Field(default=1000, ge=100, le=10000)
    poi_types: Optional[List[str]] = None

class POIResult(BaseModel):
    """POI result schema"""
    id: int
    type: str
    lat: float
    lon: float
    tags: Dict[str, Any]
    name: str
    category: str
    amenity: Optional[str] = None
    shop: Optional[str] = None
    tourism: Optional[str] = None
    leisure: Optional[str] = None
    building: Optional[str] = None
    office: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    cuisine: Optional[str] = None
    address: str

class PlaceCreate(BaseModel):
    """Place creation schema"""
    name: str = Field(..., min_length=1, max_length=200)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=300)
    tags: Optional[Dict[str, Any]] = {}

class PlaceUpdate(BaseModel):
    """Place update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lon: Optional[float] = Field(None, ge=-180, le=180)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=300)
    tags: Optional[Dict[str, Any]] = None

class PlaceResponse(BaseModel):
    """Place response schema"""
    id: str
    name: str
    lat: float
    lon: float
    description: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    saved_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

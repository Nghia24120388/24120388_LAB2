import httpx
from typing import List, Dict, Any, Optional

class NominatimService:
    """Service for interacting with Nominatim API"""
    
    BASE_URL = "https://nominatim.openstreetmap.org"
    
    @staticmethod
    async def search_places(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for places using Nominatim API"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'q': query,
                    'format': 'json',
                    'limit': limit,
                    'addressdetails': 1,
                    'extratags': 1
                }
                
                response = await client.get(
                    f"{NominatimService.BASE_URL}/search",
                    params=params,
                    headers={'User-Agent': 'OpenStreetMapApp/1.0'}
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return NominatimService._format_search_results(results)
                else:
                    raise Exception(f"Nominatim API error: {response.status_code}")
                    
        except Exception as e:
            print(f"Error searching places: {e}")
            return []
    
    @staticmethod
    async def reverse_geocode(lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get address from coordinates using Nominatim API"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'lat': lat,
                    'lon': lon,
                    'format': 'json',
                    'addressdetails': 1,
                    'extratags': 1
                }
                
                response = await client.get(
                    f"{NominatimService.BASE_URL}/reverse",
                    params=params,
                    headers={'User-Agent': 'OpenStreetMapApp/1.0'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return NominatimService._format_reverse_result(result)
                else:
                    raise Exception(f"Nominatim API error: {response.status_code}")
                    
        except Exception as e:
            print(f"Error reverse geocoding: {e}")
            return None
    
    @staticmethod
    def _format_search_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format search results for frontend"""
        formatted_results = []
        
        for result in results:
            formatted = {
                'place_id': str(result.get('place_id', '')),
                'display_name': result.get('display_name'),
                'lat': float(result.get('lat', 0)),
                'lon': float(result.get('lon', 0)),
                'type': result.get('type'),
                'importance': result.get('importance', 0),
                'address': result.get('address', {}),
                'bbox': result.get('boundingbox', [])
            }
            formatted_results.append(formatted)
        
        return formatted_results
    
    @staticmethod
    def _format_reverse_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """Format reverse geocoding result"""
        return {
            'place_id': str(result.get('place_id', '')),
            'display_name': result.get('display_name'),
            'lat': float(result.get('lat', 0)),
            'lon': float(result.get('lon', 0)),
            'type': result.get('type'),
            'address': result.get('address', {}),
            'bbox': result.get('boundingbox', [])
        }

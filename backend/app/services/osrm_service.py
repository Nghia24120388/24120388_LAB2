import httpx
from typing import List, Dict, Any, Optional, Tuple

class OSRMService:
    """Service for interacting with OSRM (Open Source Routing Machine) API"""
    
    BASE_URL = "https://router.project-osrm.org"
    
    @staticmethod
    async def get_route(start_lat: float, start_lon: float, 
                       end_lat: float, end_lon: float,
                       profile: str = "driving") -> Optional[Dict[str, Any]]:
        """Get route between two points using OSRM API"""
        try:
            coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
            
            async with httpx.AsyncClient() as client:
                params = {
                    'overview': 'full',
                    'geometries': 'geojson',
                    'steps': 'true',
                    'alternatives': 'false'
                }
                
                response = await client.get(
                    f"{OSRMService.BASE_URL}/route/v1/{profile}/{coordinates}",
                    params=params,
                    headers={'User-Agent': 'OpenStreetMapApp/1.0'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return OSRMService._format_route_result(result)
                else:
                    raise Exception(f"OSRM API error: {response.status_code}")
                    
        except Exception as e:
            print(f"Error getting route: {e}")
            return None
    
    @staticmethod
    async def get_alternative_routes(start_lat: float, start_lon: float,
                                   end_lat: float, end_lon: float,
                                   profile: str = "driving",
                                   alternatives: int = 3) -> List[Dict[str, Any]]:
        """Get multiple alternative routes"""
        try:
            coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
            
            async with httpx.AsyncClient() as client:
                params = {
                    'overview': 'full',
                    'geometries': 'geojson',
                    'steps': 'true',
                    'alternatives': str(alternatives)
                }
                
                response = await client.get(
                    f"{OSRMService.BASE_URL}/route/v1/{profile}/{coordinates}",
                    params=params,
                    headers={'User-Agent': 'OpenStreetMapApp/1.0'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return OSRMService._format_alternative_routes(result)
                else:
                    raise Exception(f"OSRM API error: {response.status_code}")
                    
        except Exception as e:
            print(f"Error getting alternative routes: {e}")
            return []
    
    @staticmethod
    async def get_distance_matrix(coordinates: List[Tuple[float, float]],
                                profile: str = "driving") -> Optional[Dict[str, Any]]:
        """Get distance matrix between multiple points"""
        try:
            # Format coordinates for OSRM
            coord_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
            
            async with httpx.AsyncClient() as client:
                params = {
                    'annotations': 'distance,duration'
                }
                
                response = await client.get(
                    f"{OSRMService.BASE_URL}/table/v1/{profile}/{coord_str}",
                    params=params,
                    headers={'User-Agent': 'OpenStreetMapApp/1.0'}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"OSRM API error: {response.status_code}")
                    
        except Exception as e:
            print(f"Error getting distance matrix: {e}")
            return None
    
    @staticmethod
    async def get_nearest_road(lat: float, lon: float,
                             profile: str = "driving") -> Optional[Dict[str, Any]]:
        """Find nearest road to a point"""
        try:
            coordinates = f"{lon},{lat}"
            
            async with httpx.AsyncClient() as client:
                params = {
                    'number': '1'
                }
                
                response = await client.get(
                    f"{OSRMService.BASE_URL}/nearest/v1/{profile}/{coordinates}",
                    params=params,
                    headers={'User-Agent': 'OpenStreetMapApp/1.0'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return OSRMService._format_nearest_result(result)
                else:
                    raise Exception(f"OSRM API error: {response.status_code}")
                    
        except Exception as e:
            print(f"Error finding nearest road: {e}")
            return None
    
    @staticmethod
    def _format_route_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """Format route result for frontend"""
        if not result.get('routes') or len(result['routes']) == 0:
            return {}
        
        route = result['routes'][0]
        
        return {
            'distance': route['distance'],  # meters
            'duration': route['duration'],  # seconds
            'geometry': route['geometry'],  # GeoJSON
            'legs': [OSRMService._format_leg(leg) for leg in route['legs']],
            'weight': route.get('weight', route['duration']),
            'weight_name': route.get('weight_name', 'duration')
        }
    
    @staticmethod
    def _format_alternative_routes(result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format multiple routes for frontend"""
        if not result.get('routes'):
            return []
        
        formatted_routes = []
        for route in result['routes']:
            formatted_route = {
                'distance': route['distance'],
                'duration': route['duration'],
                'geometry': route['geometry'],
                'legs': [OSRMService._format_leg(leg) for leg in route['legs']],
                'weight': route.get('weight', route['duration']),
                'weight_name': route.get('weight_name', 'duration')
            }
            formatted_routes.append(formatted_route)
        
        return formatted_routes
    
    @staticmethod
    def _format_leg(leg: Dict[str, Any]) -> Dict[str, Any]:
        """Format route leg for frontend"""
        return {
            'distance': leg['distance'],
            'duration': leg['duration'],
            'summary': leg.get('summary', ''),
            'steps': [OSRMService._format_step(step) for step in leg.get('steps', [])]
        }
    
    @staticmethod
    def _format_step(step: Dict[str, Any]) -> Dict[str, Any]:
        """Format route step for frontend"""
        maneuver = step.get('maneuver', {})
        
        return {
            'distance': step['distance'],
            'duration': step['duration'],
            'geometry': step['geometry'],
            'maneuver': {
                'type': maneuver.get('type', ''),
                'instruction': maneuver.get('instruction', ''),
                'bearing_before': maneuver.get('bearing_before', 0),
                'bearing_after': maneuver.get('bearing_after', 0),
                'location': maneuver.get('location', [0, 0])
            },
            'name': step.get('name', ''),
            'mode': step.get('mode', 'driving')
        }
    
    @staticmethod
    def _format_nearest_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """Format nearest road result"""
        if not result.get('waypoints') or len(result['waypoints']) == 0:
            return {}
        
        waypoint = result['waypoints'][0]
        
        return {
            'location': waypoint['location'],
            'name': waypoint.get('name', ''),
            'distance': waypoint.get('distance', 0)
        }

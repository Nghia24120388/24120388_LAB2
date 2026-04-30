import httpx
from typing import List, Dict, Any, Optional

class OverpassService:
    """Service for interacting with Overpass API"""
    
    BASE_URL = "https://overpass-api.de/api/interpreter"
    
    @staticmethod
    async def get_nearby_pois(lat: float, lon: float, radius: int = 1000, 
                           poi_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get nearby POIs using Overpass API"""
        try:
            # Default POI types if none specified
            if not poi_types:
                poi_types = [
                    'amenity', 'shop', 'tourism', 'leisure', 
                    'building', 'office', 'craft', 'emergency'
                ]
            
            # Build Overpass QL query
            if len(poi_types) == 1:
                # Single POI type - simple query
                poi_filter = f'["{poi_types[0]}"]'
                query = f"""
                [out:json][timeout:25];
                (
                  node{poi_filter}(around:{radius},{lat},{lon});
                  way{poi_filter}(around:{radius},{lat},{lon});
                  relation{poi_filter}(around:{radius},{lat},{lon});
                );
                out geom;
                """
            else:
                # Multiple POI types - use union approach
                poi_queries = []
                for poi_type in poi_types:
                    poi_queries.append(f"""
                      node["{poi_type}"](around:{radius},{lat},{lon});
                      way["{poi_type}"](around:{radius},{lat},{lon});
                      relation["{poi_type}"](around:{radius},{lat},{lon});
                    """)
                
                query = f"""
                [out:json][timeout:30];
                (
                    {"".join(poi_queries)}
                );
                out geom;
                """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    OverpassService.BASE_URL,
                    data=query,
                    headers={'User-Agent': 'OpenStreetMapApp/1.0'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    formatted_results = OverpassService._format_poi_results(result)
                    print(f"Overpass query returned {len(formatted_results)} POIs for types: {poi_types}")
                    return formatted_results
                else:
                    print(f"Overpass API error: {response.status_code}, Query: {query}")
                    raise Exception(f"Overpass API error: {response.status_code}")
                    
        except Exception as e:
            print(f"Error getting nearby POIs: {e}")
            return []
    
    @staticmethod
    async def get_pois_by_type(poi_type: str, lat: float, lon: float, 
                              radius: int = 1000) -> List[Dict[str, Any]]:
        """Get POIs by specific type"""
        try:
            query = f"""
            [out:json][timeout:25];
            (
              node["{poi_type}"](around:{radius},{lat},{lon});
              way["{poi_type}"](around:{radius},{lat},{lon});
              relation["{poi_type}"](around:{radius},{lat},{lon});
            );
            out geom;
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    OverpassService.BASE_URL,
                    data=query,
                    headers={'User-Agent': 'OpenStreetMapApp/1.0'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return OverpassService._format_poi_results(result)
                else:
                    raise Exception(f"Overpass API error: {response.status_code}")
                    
        except Exception as e:
            print(f"Error getting POIs by type: {e}")
            return []
    
    @staticmethod
    def _format_poi_results(result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format POI results for frontend"""
        formatted_results = []
        
        elements = result.get('elements', [])
        
        for element in elements:
            # Get coordinates
            lat = lon = None
            if element['type'] == 'node':
                lat = element.get('lat')
                lon = element.get('lon')
            elif element['type'] in ['way', 'relation']:
                # For ways and relations, get center point
                bounds = element.get('bounds')
                if bounds:
                    lat = (bounds['minlat'] + bounds['maxlat']) / 2
                    lon = (bounds['minlon'] + bounds['maxlon']) / 2
            
            if lat and lon:
                tags = element.get('tags', {})
                
                formatted = {
                    'id': element.get('id'),
                    'type': element['type'],
                    'lat': lat,
                    'lon': lon,
                    'tags': tags,
                    'name': tags.get('name', 'Unknown'),
                    'category': OverpassService._get_poi_category(tags),
                    'amenity': tags.get('amenity'),
                    'shop': tags.get('shop'),
                    'tourism': tags.get('tourism'),
                    'leisure': tags.get('leisure'),
                    'building': tags.get('building'),
                    'office': tags.get('office'),
                    'phone': tags.get('phone'),
                    'website': tags.get('website'),
                    'opening_hours': tags.get('opening_hours'),
                    'cuisine': tags.get('cuisine'),
                    'address': OverpassService._format_address(tags)
                }
                
                formatted_results.append(formatted)
        
        return formatted_results
    
    @staticmethod
    def _get_poi_category(tags: Dict[str, Any]) -> str:
        """Determine POI category from tags"""
        if 'amenity' in tags:
            return tags['amenity']
        elif 'shop' in tags:
            return 'shop'
        elif 'tourism' in tags:
            return tags['tourism']
        elif 'leisure' in tags:
            return tags['leisure']
        elif 'building' in tags:
            return tags['building']
        elif 'office' in tags:
            return tags['office']
        elif 'craft' in tags:
            return tags['craft']
        elif 'emergency' in tags:
            return tags['emergency']
        else:
            return 'unknown'
    
    @staticmethod
    def _format_address(tags: Dict[str, Any]) -> str:
        """Format address from tags"""
        address_parts = []
        
        if 'addr:housenumber' in tags:
            address_parts.append(tags['addr:housenumber'])
        if 'addr:street' in tags:
            address_parts.append(tags['addr:street'])
        if 'addr:city' in tags:
            address_parts.append(tags['addr:city'])
        if 'addr:postcode' in tags:
            address_parts.append(tags['addr:postcode'])
        
        return ', '.join(address_parts)

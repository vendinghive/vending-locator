import requests
import time
import random
from typing import List, Dict, Optional, Tuple
from django.conf import settings
import google.generativeai as genai

class FootTrafficEstimator:
    @staticmethod
    def estimate_foot_traffic(lat: float, lon: float, category: str) -> str:
        """
        Estimate foot traffic based on OSM data and location characteristics
        Returns: 'Low', 'Moderate', or 'High'
        """
        try:
            score = 0
            
            # Check proximity to public transport
            transport_score = FootTrafficEstimator._check_transport_proximity(lat, lon)
            score += transport_score
            
            # Check residential density
            residential_score = FootTrafficEstimator._check_residential_density(lat, lon)
            score += residential_score
            
            # Check commercial activity
            commercial_score = FootTrafficEstimator._check_commercial_activity(lat, lon)
            score += commercial_score
            
            # Category-based adjustment
            category_score = FootTrafficEstimator._get_category_score(category)
            score += category_score
            
            # Convert score to traffic level
            if score >= 7:
                return 'High'
            elif score >= 4:
                return 'Moderate'
            else:
                return 'Low'
                
        except Exception as e:
            print(f"Foot traffic estimation error: {str(e)}")
            return 'Low'  # Default fallback
    
    @staticmethod
    def _check_transport_proximity(lat: float, lon: float) -> int:
        """Check proximity to public transport hubs"""
        try:
            query = f"""
            [out:json][timeout:15];
            (
              node["public_transport"](around:500,{lat},{lon});
              node["railway"="station"](around:500,{lat},{lon});
              node["amenity"="bus_station"](around:500,{lat},{lon});
            );
            out count;
            """
            
            response = requests.post(
                "https://overpass-api.de/api/interpreter",
                data=query,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('elements', []))
                return min(3, count)  # Max 3 points
            return 0
            
        except Exception:
            return 0
    
    @staticmethod
    def _check_residential_density(lat: float, lon: float) -> int:
        """Check density of residential buildings"""
        try:
            query = f"""
            [out:json][timeout:15];
            (
              way["building"="residential"](around:800,{lat},{lon});
              way["building"="apartments"](around:800,{lat},{lon});
            );
            out count;
            """
            
            response = requests.post(
                "https://overpass-api.de/api/interpreter",
                data=query,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('elements', []))
                if count > 20:
                    return 2
                elif count > 10:
                    return 1
            return 0
            
        except Exception:
            return 0
    
    @staticmethod
    def _check_commercial_activity(lat: float, lon: float) -> int:
        """Check commercial activity in the area"""
        try:
            query = f"""
            [out:json][timeout:15];
            (
              node["shop"](around:300,{lat},{lon});
              node["amenity"~"^(restaurant|cafe|fast_food|bar)$"](around:300,{lat},{lon});
            );
            out count;
            """
            
            response = requests.post(
                "https://overpass-api.de/api/interpreter",
                data=query,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('elements', []))
                if count > 15:
                    return 3
                elif count > 8:
                    return 2
                elif count > 3:
                    return 1
            return 0
            
        except Exception:
            return 0
    
    @staticmethod
    def _get_category_score(category: str) -> int:
        """Assign score based on business category"""
        high_traffic_categories = ['mall', 'shopping', 'restaurant', 'fast_food', 'cinema']
        medium_traffic_categories = ['gym', 'hospital', 'school', 'office']
        
        category_lower = category.lower()
        
        if any(cat in category_lower for cat in high_traffic_categories):
            return 2
        elif any(cat in category_lower for cat in medium_traffic_categories):
            return 1
        return 0

class LocationFinderService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            print(f"Failed to initialize Gemini AI: {str(e)}")
            self.model = None
    
    def validate_zip_code(self, zip_code: str) -> bool:
        """Validate if zip code exists using OpenStreetMap"""
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{zip_code}, USA",
                'format': 'json',
                'countrycodes': 'us',
                'limit': 1
            }
            headers = {'User-Agent': 'VendingLocationFinder/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return len(data) > 0
            
        except Exception as e:
            print(f"Zip code validation error: {str(e)}")
            return False
    
    def get_coordinates_from_zip(self, zip_code: str) -> Optional[Tuple[float, float]]:
        """Get latitude and longitude from zip code"""
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{zip_code}, USA",
                'format': 'json',
                'countrycodes': 'us',
                'limit': 1
            }
            headers = {'User-Agent': 'VendingLocationFinder/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            return None
            
        except Exception as e:
            print(f"Coordinates error: {str(e)}")
            return None
    
    # def find_nearby_places(self, lat: float, lon: float, machine_type: str) -> List[Dict]:
    #     """Find nearby places suitable for vending machines"""
    #     try:
    #         # Define place types based on machine type
    #         if machine_type.lower() == "vending machine":
    #             place_types = {
    #                 "leisure=fitness_centre": "Gym",
    #                 "office=*": "Office",
    #                 "amenity=school": "Education",
    #                 "amenity=university": "Education",
    #                 "amenity=hospital": "Healthcare",
    #                 "amenity=cafe": "Food",
    #                 "amenity=fast_food": "Food",
    #                 "shop=mall": "Shopping"
    #             }
    #         else:  # Claw Machine
    #             place_types = {
    #                 "leisure=amusement_arcade": "Entertainment",
    #                 "amenity=cinema": "Entertainment",
    #                 "leisure=bowling_alley": "Entertainment",
    #                 "shop=mall": "Shopping",
    #                 "amenity=restaurant": "Food",
    #                 "amenity=fast_food": "Food",
    #                 "amenity=cafe": "Food"
    #             }
            
    #         categorized_places = {category: [] for category in set(place_types.values())}
    #         radius = 5000
    #         max_per_place_type = 3
            
    #         for place_type, category in place_types.items():
    #             try:
    #                 query = f"""
    #                 [out:json][timeout:25];
    #                 (
    #                 node["{place_type.split('=')[0]}"="{place_type.split('=')[1]}"](around:{radius},{lat},{lon});
    #                 way["{place_type.split('=')[0]}"="{place_type.split('=')[1]}"](around:{radius},{lat},{lon});
    #                 );
    #                 out center meta;
    #                 """
                    
    #                 response = requests.post(
    #                     "https://overpass-api.de/api/interpreter",
    #                     data=query,
    #                     timeout=30
    #                 )
    #                 response.raise_for_status()
                    
    #                 data = response.json()
    #                 places_added = 0
                    
    #                 for element in data.get('elements', []):
    #                     if places_added >= max_per_place_type:
    #                         break
                        
    #                     name = element.get('tags', {}).get('name', 'Unknown Location')
    #                     if name == 'Unknown Location':
    #                         continue
                        
    #                     # Get coordinates
    #                     if 'lat' in element and 'lon' in element:
    #                         place_lat, place_lon = element['lat'], element['lon']
    #                     elif 'center' in element:
    #                         place_lat, place_lon = element['center']['lat'], element['center']['lon']
    #                     else:
    #                         continue
                        
    #                     tags = element.get('tags', {})
                        
    #                     # Extract additional information
    #                     phone = self._extract_phone(tags)
    #                     email = self._extract_email(tags)
    #                     business_hours = self._extract_business_hours(tags)
    #                     foot_traffic = FootTrafficEstimator.estimate_foot_traffic(
    #                         place_lat, place_lon, category
    #                     )
                        
    #                     place_info = {
    #                         'name': name,
    #                         'category': self._determine_detailed_category(tags),
    #                         'address': self._get_address_from_coords(place_lat, place_lon),
    #                         'lat': place_lat,
    #                         'lon': place_lon,
    #                         'phone': phone,
    #                         'email': email,
    #                         'business_hours': business_hours,
    #                         'foot_traffic': foot_traffic,
    #                         'type_category': category
    #                     }
                        
    #                     # Avoid duplicates
    #                     if not any(p['name'] == name for p in categorized_places[category]):
    #                         categorized_places[category].append(place_info)
    #                         places_added += 1
                    
    #                 time.sleep(0.5)  # Rate limiting
                    
    #             except Exception as e:
    #                 print(f"Place type search error: {str(e)}")
    #                 continue
            
    #         # Select diverse places
    #         final_places = []
            
    #         # First, ensure one place from each category
    #         for category, places in categorized_places.items():
    #             if places:
    #                 final_places.append(places[0])
            
    #         # Add more places if we have less than 5
    #         if len(final_places) < 5:
    #             additional_places = []
    #             for category, places in categorized_places.items():
    #                 if len(places) > 1:
    #                     additional_places.extend(places[1:])
                
    #             random.shuffle(additional_places)
    #             for place in additional_places:
    #                 if len(final_places) >= 5:
    #                     break
    #                 if not any(p['name'] == place['name'] for p in final_places):
    #                     final_places.append(place)
            
    #         # Fallback if we have too few places
    #         if len(final_places) < 2:
    #             return self._fallback_search(lat, lon)
            
    #         return final_places[:5]  # Return max 5 places
            
    #     except Exception as e:
    #         print(f"Find nearby places error: {str(e)}")
    #         return self._fallback_search(lat, lon)
    
    # def find_nearby_places(self, lat: float, lon: float, machine_type: str) -> List[Dict]:
    #     """Find nearby places suitable for vending machines"""
    #     try:
    #         # Define place types based on machine type
    #         if machine_type.lower() == "vending machine":
    #             place_types = {
    #                 "leisure": "fitness_centre",
    #                 "amenity": "school",
    #                 "amenity": "university", 
    #                 "amenity": "hospital",
    #                 "amenity": "cafe",
    #                 "amenity": "fast_food",
    #                 "shop": "mall"
    #             }
    #         else:  # Claw Machine
    #             place_types = {
    #                 "amenity": "cinema",
    #                 "leisure": "bowling_alley",
    #                 "shop": "mall",
    #                 "amenity": "restaurant",
    #                 "amenity": "fast_food",
    #                 "amenity": "cafe"
    #             }
            
    #         all_places = []
    #         radius = 5000
            
    #         for key, value in place_types.items():
    #             try:
    #                 query = f"""
    #                 [out:json][timeout:25];
    #                 (
    #                 node["{key}"="{value}"](around:{radius},{lat},{lon});
    #                 way["{key}"="{value}"](around:{radius},{lat},{lon});
    #                 );
    #                 out center meta;
    #                 """
                    
    #                 response = requests.post(
    #                     "https://overpass-api.de/api/interpreter",
    #                     data=query,
    #                     timeout=30
    #                 )
                    
    #                 if response.status_code == 200:
    #                     data = response.json()
                        
    #                     for element in data.get('elements', [])[:2]:  # Limit to 2 per type
    #                         name = element.get('tags', {}).get('name', 'Unknown Location')
    #                         if name == 'Unknown Location':
    #                             continue
                            
    #                         # Get coordinates
    #                         if 'lat' in element and 'lon' in element:
    #                             place_lat, place_lon = element['lat'], element['lon']
    #                         elif 'center' in element:
    #                             place_lat, place_lon = element['center']['lat'], element['center']['lon']
    #                         else:
    #                             continue
                            
    #                         tags = element.get('tags', {})
                            
    #                         place_info = {
    #                             'name': name,
    #                             'category': self._determine_detailed_category(tags),
    #                             'address': self._get_address_from_coords(place_lat, place_lon),
    #                             'lat': place_lat,
    #                             'lon': place_lon,
    #                             'phone': self._extract_phone(tags),
    #                             'email': self._extract_email(tags),
    #                             'business_hours': self._extract_business_hours(tags),
    #                             'foot_traffic': FootTrafficEstimator.estimate_foot_traffic(
    #                                 place_lat, place_lon, value
    #                             )
    #                         }
                            
    #                         # Avoid duplicates
    #                         if not any(p['name'] == name for p in all_places):
    #                             all_places.append(place_info)
                    
    #                 time.sleep(1)  # Rate limiting
                    
    #             except Exception as e:
    #                 print(f"Place type search error for {key}={value}: {str(e)}")
    #                 continue
            
    #         # Return up to 5 places
    #         return all_places[:5] if all_places else self._fallback_search(lat, lon)
            
    #     except Exception as e:
    #         print(f"Find nearby places error: {str(e)}")
    #         return self._fallback_search(lat, lon)

    def find_nearby_places(self, lat: float, lon: float, machine_type: str, radius_miles: int = 5) -> List[Dict]:

        """Find nearby places suitable for vending machines"""
        try:
            # Convert miles to meters
            radius = radius_miles * 1609  # 1 mile = 1609 meters
            
            # Define place types based on machine type
            if machine_type == "Snack & Drink Machines":
                place_types = {
                    "amenity": ["school", "university", "hospital", "office"],
                    "leisure": ["fitness_centre"],
                    "building": ["office"]
                }
            elif machine_type == "Claw Machine":
                place_types = {
                    "amenity": ["cinema", "restaurant", "fast_food", "cafe"],
                    "leisure": ["bowling_alley", "amusement_arcade"],
                    "shop": ["mall"]
                }
            elif machine_type == "Cotton Candy Machines":
                place_types = {
                    "amenity": ["cinema", "theatre"],
                    "leisure": ["amusement_arcade", "park"],
                    "shop": ["mall"]
                }
            elif machine_type == "Hot Dog Vending":
                place_types = {
                    "amenity": ["university", "school", "hospital"],
                    "leisure": ["stadium", "sports_centre"],
                    "building": ["office"]
                }
            elif machine_type == "Fresh Food Market Machines":
                place_types = {
                    "amenity": ["hospital", "university", "office"],
                    "building": ["office"],
                    "leisure": ["fitness_centre"]
                }
            else:
                # Default fallback
                place_types = {
                    "amenity": ["school", "restaurant", "cafe"],
                    "leisure": ["fitness_centre"],
                    "shop": ["mall"]
                }
            
            all_places = []
            
            for key, values in place_types.items():
                for value in values:
                    try:
                        query = f"""
                        [out:json][timeout:25];
                        (
                            node["{key}"="{value}"](around:{radius},{lat},{lon});
                            way["{key}"="{value}"](around:{radius},{lat},{lon});
                        );
                        out center meta;
                        """
                        
                        response = requests.post(
                            "https://overpass-api.de/api/interpreter",
                            data=query,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            for element in data.get('elements', [])[:2]:  # Limit to 2 per type
                                name = element.get('tags', {}).get('name', 'Unknown Location')
                                if name == 'Unknown Location':
                                    continue
                                
                                # Get coordinates
                                if 'lat' in element and 'lon' in element:
                                    place_lat, place_lon = element['lat'], element['lon']
                                elif 'center' in element:
                                    place_lat, place_lon = element['center']['lat'], element['center']['lon']
                                else:
                                    continue
                                
                                tags = element.get('tags', {})
                                
                                place_info = {
                                    'name': name,
                                    'category': self._determine_detailed_category(tags),
                                    'address': self._get_address_from_coords(place_lat, place_lon),
                                    'lat': place_lat,
                                    'lon': place_lon,
                                    'phone': self._extract_phone(tags),
                                    'email': self._extract_email(tags),
                                    'business_hours': self._extract_business_hours(tags)
                                    # Removed foot_traffic
                                }
                                
                                # Avoid duplicates
                                if not any(p['name'] == name for p in all_places):
                                    all_places.append(place_info)
                        
                        time.sleep(0.5)  # Rate limiting
                        
                    except Exception as e:
                        print(f"Place type search error for {key}={value}: {str(e)}")
                        continue
            
            # Return up to 10 places
            return all_places[:10] if all_places else self._fallback_search(lat, lon)
            
        except Exception as e:
            print(f"Find nearby places error: {str(e)}")
            return self._fallback_search(lat, lon)     
    def _extract_phone(self, tags: Dict) -> str:
        """Extract phone number from OSM tags"""
        phone_keys = ['phone', 'contact:phone', 'telephone']
        for key in phone_keys:
            if key in tags:
                return tags[key]
        return ''
    
    def _extract_email(self, tags: Dict) -> str:
        """Extract email from OSM tags"""
        email_keys = ['email', 'contact:email']
        for key in email_keys:
            if key in tags:
                return tags[key]
        return ''
    
    def _extract_business_hours(self, tags: Dict) -> str:
        """Extract business hours from OSM tags"""
        if 'opening_hours' in tags:
            return tags['opening_hours']
        return '9:00-17:00'  # Default business hours
    
    def _determine_detailed_category(self, tags: Dict) -> str:
        """Determine detailed category from OSM tags"""
        if tags.get('amenity') == 'cafe':
            return 'Cafe'
        elif tags.get('amenity') == 'restaurant':
            return 'Restaurant'
        elif tags.get('amenity') == 'fast_food':
            return 'Fast Food'
        elif tags.get('leisure') == 'fitness_centre':
            return 'Gym/Fitness Center'
        elif tags.get('amenity') in ['school', 'university']:
            return 'Educational Institution'
        elif 'office' in tags:
            return 'Office Building'
        elif tags.get('amenity') == 'hospital':
            return 'Healthcare Facility'
        elif tags.get('shop') == 'mall':
            return 'Shopping Mall'
        elif tags.get('amenity') == 'cinema':
            return 'Cinema'
        elif tags.get('leisure') == 'bowling_alley':
            return 'Entertainment Venue'
        else:
            return 'Business Location'
    
    def _get_address_from_coords(self, lat: float, lon: float) -> str:
        """Get address from coordinates"""
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json'
            }
            headers = {'User-Agent': 'VendingLocationFinder/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get('display_name', 'Address not available')
            
        except Exception:
            return 'Address not available'
    
    def _fallback_search(self, lat: float, lon: float) -> List[Dict]:
        """Fallback search using Nominatim"""
        try:
            places = []
            search_terms = ['restaurant', 'cafe', 'gym', 'office', 'school']
            
            for term in search_terms:
                if len(places) >= 5:
                    break
                
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': term,
                    'format': 'json',
                    'lat': lat,
                    'lon': lon,
                    'radius': 5000,
                    'limit': 1
                }
                headers = {'User-Agent': 'VendingLocationFinder/1.0'}
                
                try:
                    response = requests.get(url, params=params, headers=headers, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    
                    for item in data:
                        if len(places) >= 5:
                            break
                        
                        item_lat, item_lon = float(item['lat']), float(item['lon'])
                        foot_traffic = FootTrafficEstimator.estimate_foot_traffic(
                            item_lat, item_lon, term
                        )
                        
                        places.append({
                            'name': item.get('display_name', 'Unknown Location').split(',')[0],
                            'category': term.title(),
                            'address': item.get('display_name', 'Address not available'),
                            'lat': item_lat,
                            'lon': item_lon,
                            'phone': '',
                            'email': '',
                            'business_hours': '9:00-17:00',
                            'foot_traffic': foot_traffic
                        })
                    
                    time.sleep(0.5)
                except Exception:
                    continue
            
            return places if places else [{
                'name': 'Local Business District',
                'category': 'Business Area',
                'address': f'Near {lat:.4f}, {lon:.4f}',
                'lat': lat,
                'lon': lon,
                'phone': '',
                'email': '',
                'business_hours': '9:00-17:00',
                'foot_traffic': 'Low'
            }]
            
        except Exception:
            return [{
                'name': 'Local Business District',
                'category': 'Business Area',
                'address': f'Near {lat:.4f}, {lon:.4f}',
                'lat': lat,
                'lon': lon,
                'phone': '',
                'email': '',
                'business_hours': '9:00-17:00',
                'foot_traffic': 'Low'
            }]
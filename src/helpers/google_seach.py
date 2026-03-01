import googlemaps
from django.conf import settings

def get_gmaps_client():
    return googlemaps.Client(key=settings.GOOGLE_PLACES_API_KEY)

# helpers/google_places.py

def search_restaurants(query):
    gmaps = get_gmaps_client()
    results = gmaps.places(query=query, type='restaurant')
    
    restaurants = []
    for place in results.get('results', []):
        restaurants.append({
            'place_id': place.get('place_id'),
            'name': place.get('name'),
            'address': place.get('formatted_address'),
            'rating': place.get('rating'),
            'user_ratings_total': place.get('user_ratings_total'),
        })
    
    return restaurants


def get_restaurant_details(place_id):
    gmaps = get_gmaps_client()
    detail = gmaps.place(place_id=place_id).get('result', None)
    if not detail:
        return None
    
    return {
        'place_id': detail.get('place_id'),
        'name': detail.get('name'),
        'address': detail.get('formatted_address'),
        'phone_number': detail.get('international_phone_number'),
        'business_status': detail.get('business_status'),
        'website': detail.get('website'),
        'google_maps_url': detail.get('url'),
        'delivery': detail.get('delivery'),
        'dine_in': detail.get('dine_in'),
        'serves_beer': detail.get('serves_beer'),
        'serves_wine': detail.get('serves_wine'),
        'serves_breakfast': detail.get('serves_breakfast'),
        'serves_dinner': detail.get('serves_dinner'),
        'serves_lunch': detail.get('serves_lunch'),
        'serves_vegetarian_food': detail.get('serves_vegetarian_food'),
        'takeout': detail.get('takeout'),
        'types': ", ".join(detail.get('types', [])),
        'wheelchair_accessible_entrance': detail.get('wheelchair_accessible_entrance'),
        'reservable': detail.get('reservable'),
        'rating': detail.get('rating'),
        'price_level': detail.get('price_level'),
        'user_ratings_total': detail.get('user_ratings_total'),
    }
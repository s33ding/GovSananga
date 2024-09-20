import os
import googlemaps
import time

# Global Variables
api_key = os.environ.get("GCP_KEY")

gmaps = googlemaps.Client(key=api_key)

location = (37.7749, -122.4194)  # San Francisco Coordinates
radius = 1000  # Search radius in meters
place_type = 'hospitals'  # Type of places to search
test_mode = True  # Set to True for testing purposes, False for production

def fetch_places():
    """Fetch places using Google Places API and handle pagination."""
    global location, radius, place_type, gmaps, test_mode  # Declare global variables
    places = []

    # Make the API request
    results = gmaps.places_nearby(location=location, radius=radius, type=place_type)
    places.extend(results.get('results', []))

    # Handle pagination
    while 'next_page_token' in results:
        if test_mode and len(places) >= 5:  # Limit to 5 places in test mode
            break
        time.sleep(2)  # Must wait before making the next request
        results = gmaps.places_nearby(page_token=results['next_page_token'])
        places.extend(results.get('results', []))

    return places[:5] if test_mode else places  # Limit to 5 places in test mode

def fetch_place_details(place_id):
    """Fetch place details including reviews using Google Places API."""
    global gmaps, test_mode  # Declare global variable
    place_details = gmaps.place(place_id=place_id)
    return place_details.get('result', {})

def extract_reviews(places):
    """Extract reviews for each place."""
    global test_mode  # Declare global variable
    all_reviews = {}
    for place in places:
        place_id = place.get('place_id')
        if place_id:
            details = fetch_place_details(place_id)
            reviews = details.get('reviews', [])
            if test_mode:
                reviews = reviews[:2]  # Limit to 2 reviews per place in test mode
            all_reviews[place.get('name')] = [review.get('text') for review in reviews]

        if test_mode and len(all_reviews) >= 3:  # Limit to 3 places with reviews in test mode
            break

    return all_reviews

# Example Usage:
# Fetch places using global variables
places = fetch_places()

# Extract reviews
reviews = extract_reviews(places)

# Print the reviews
for place, review_list in reviews.items():
    print(f"Place: {place}")
    for review in review_list:
        print(f" - Review: {review}")

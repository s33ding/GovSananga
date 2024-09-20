import googlemaps
import time
import os
import requests

# Fetch the API key from environment variables
api_key = os.getenv("GCP_KEY")

# Ensure the API key is available
if not api_key:
    raise ValueError("API Key not found. Make sure 'GCP_KEY' is set in environment variables.")

gmaps = googlemaps.Client(key=api_key)

def get_street_view_image(api_key, location, heading=180, pitch=0, fov=90, output_image="street_view_image.jpg"):
    """
    Fetches a Street View image from the Google Street View API.

    Parameters:
    - api_key (str): Google API key.
    - location (str): Latitude and longitude of the location or an address.
    - heading (int): Compass heading of the camera (0 - 360).
    - pitch (int): Up or down angle relative to the Street View vehicle's position (-90 to 90).
    - fov (int): Field of view, a zoom parameter (default is 90 degrees).
    - output_image (str): Filename to save the image as (default: street_view_image.jpg).

    Returns:
    - None: Saves the image to the output_image path.
    """

    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": "2048x2048",  # Image size
        "location": location,  # Address or lat,lng
        "heading": heading,  # Camera heading direction
        "pitch": pitch,  # Camera pitch
        "fov": fov,  # Field of view
        "key": api_key,  # API key
    }

    # Print URL for manual testing in the browser
    request_url = requests.Request('GET', base_url, params=params).prepare().url
    print(f"Request URL: {request_url}")

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        with open(output_image, "wb") as file:
            file.write(response.content)
        print(f"Street View image saved as {output_image}")
    else:
        print(f"Failed to fetch the image. HTTP Status Code: {response.status_code}")
        print(f"Response: {response.text}")


if __name__ == "__main__":
    # Use a different location as an example
    location = "-15.782750004942436,-47.99919615052566"  # Latitude,Longitude example in Brasília
    get_street_view_image(api_key, location, heading=180, pitch=0)


import googlemaps
import time
import os
import requests
from shared_func.secret_manager_func import get_secret
import shutil
import math
from PIL import Image
from io import BytesIO


# Fetch the API key once and reuse it
gcp_api_key = get_secret("s33ding").get("gcp")

# Ensure the API key is available
if not gcp_api_key:
    raise ValueError("API Key not found")

def create_clean_folder(folder_name):
    # Check if the folder exists
    if os.path.exists(folder_name):
        # Remove the folder and its contents
        shutil.rmtree(folder_name)
    # Create the folder again, now empty
    os.makedirs(folder_name, exist_ok=True)
    
import requests
from PIL import Image
from io import BytesIO

def get_street_view_image(location, heading, pitch=0, fov=90, output_image="street_view_image.jpg"):
    global response
    """
    Fetches a Google Street View image for the given location and heading, and saves it if valid.

    Parameters:
    - location: tuple of latitude and longitude (lat, lng)
    - heading: float - the compass direction of the camera, in degrees
    - pitch: float - the up or down angle of the camera, in degrees
    - fov: float - the field of view of the camera, in degrees
    - output_image: str - the path to save the image file

    Returns:
    - None
    """
    # Prepare the parameters for the API request
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": "2048x2048",  # Image size
        "location": f"{location[0]},{location[1]}",  # Address or lat,lng
        "heading": heading,  # Camera heading direction
        "pitch": pitch,  # Camera pitch
        "fov": fov,  # Field of view
        "key": gcp_api_key,  # API key
    }

    # Print URL for manual testing in the browser
    request_url = requests.Request('GET', base_url, params=params).prepare().url
    print(f"Request URL: {request_url}")

    # Send the request to fetch the Street View image
    response = requests.get(base_url, params=params)

    if response.status_code == 200 and response.content:
        # Open the image from response content
        image = Image.open(BytesIO(response.content))

        # Check for 'Sorry, we have no imagery here' using specific pixels
        if image.getbbox() and is_image_valid(image):
            with open(output_image, "wb") as file:
                file.write(response.content)
            print(f"Street View image saved as {output_image}")
            return True
        else:
            print("No valid Street View imagery available for this location.")
    else:
        print(f"Failed to fetch a valid image. HTTP Status Code: {response.status_code}")
        print(f"Response: {response.text if response.content else 'No content returned'}")

def is_image_valid(image):
    """
    Check if the image is valid and does not contain the 'no imagery' message.

    Parameters:
    - image: PIL Image object

    Returns:
    - bool: True if the image is valid, False otherwise
    """
    # Convert image to grayscale for better processing
    grayscale_image = image.convert("L")
    
    # Sample pixels from the center to check for uniform background
    width, height = grayscale_image.size
    center_region = grayscale_image.crop((width // 4, height // 4, 3 * width // 4, 3 * height // 4))

    # Check if the center region is nearly uniform
    # Threshold depends on specific images; adjust if needed
    return not is_uniform_image(center_region)

def is_uniform_image(image, threshold=15):
    """
    Check if an image is almost uniform in color.

    Parameters:
    - image: PIL Image object in grayscale mode
    - threshold: int - The maximum variance allowed to consider the image uniform

    Returns:
    - bool: True if the image is uniform, False otherwise
    """
    # Get pixel values
    pixels = list(image.getdata())

    # Calculate standard deviation to check uniformity
    mean_pixel = sum(pixels) / len(pixels)
    variance = sum((p - mean_pixel) ** 2 for p in pixels) / len(pixels)
    stddev = variance ** 0.5

    # If standard deviation is below the threshold, the image is uniform
    return stddev < threshold

def automate_street_view_images(df, group_name):
    # Filter the DataFrame based on the group
    filtered_df = df[df["group"] == group_name].reset_index(drop=True)

    # Create the output directory if it doesn't exist
    folder_name = f"output/street-view-gr-{group_name}"
    create_clean_folder(folder_name)
    print(f"Output directory created: {folder_name}")

    # Iterate through the DataFrame and call the get_street_view_image function for each pair of coordinates
    for i,val in filtered_df.iterrows():
        location = filtered_df["coordinates"].iloc[i]
        next_location = filtered_df["next_coordinates"].iloc[i]
        order = filtered_df["order"].iloc[i]
        # Generate the image with the calculated heading
        if next_location is not None:
            get_street_view_image(location=location, heading=0, output_image=f"{folder_name}/{order}-a-0.jpg")
            get_street_view_image(location=location, heading=90, output_image=f"{folder_name}/{order}-b-90.jpg")
            get_street_view_image(location=location, heading=180, output_image=f"{folder_name}/{order}-c-180.jpg")
            get_street_view_image(location=location, heading=270, output_image=f"{folder_name}/{order}-d-270.jpg")
    return filtered_df



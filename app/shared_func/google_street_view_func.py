import config
import googlemaps
import time
import os
import requests
from shared_func.secret_manager_func import get_secret
from shared_func.lambda_func import invoke_lambda
import shutil
import math
from PIL import Image
from io import BytesIO
import boto3

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb',region_name=config.region_name)
print(region_name)

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
    

def get_street_view_image(group_name, location, heading, pitch=0, fov=config.gsv_fov, order=None,delete=True,verbose=False):
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

    folder_name = f"output/street-view/group-{group_name}"                           
    output_image = f"{folder_name}/order-{order}-heading-{heading}.jpg"
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

    # Send the request to fetch the Street View image
    response = requests.get(base_url, params=params)

    if response.status_code == 200 and response.content:
        # Open the image from response content
        image = Image.open(BytesIO(response.content))

        # Check for 'Sorry, we have no imagery here' using specific pixels
        if image.getbbox() and is_image_valid(image):
            with open(output_image, "wb") as file:
                file.write(response.content)
            if verbose:
                print(f"Street View image saved as {output_image}")
            if delete:
                os.system(f"rm {output_image}")
            return request_url 
        else:
            if verbose:
                print("No valid Street View imagery available for this location.")
            return False
    else:
        if verbose:
            print(f"Failed to fetch a valid image. HTTP Status Code: {response.status_code}")
            print(f"Response: {response.text if response.content else 'No content returned'}")
        return False

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

def upload_to_s3(file_path, bucket_name, key_name):
    # Initialize the S3 client
    s3_client = boto3.client("s3", region_name=config.region_name)

    s3_path = f"s3://{bucket_name}/{key_name}"
    s3_client.upload_file(file_path, bucket_name, key_name)
    print(f"Uploaded {file_path} to {s3_path}")

def automate_street_view_images(df, group_name,verbose=False):                                     
    # Filter DataFrame based on the specified group name and reset index
    filtered_df = df[df["group"] == group_name].reset_index(drop=True)
    
    # Define output directory and ensure it's clean
    folder_name = f"output/street-view/group-{group_name}"                           
    create_clean_folder(folder_name)

    if verbose:
        print(f"Output directory created: {folder_name}")

    # Initialize s3_path column
    filtered_df["s3_path"] = None

    # Iterate over each row in the filtered DataFrame
    for i, row in filtered_df.iterrows():
        location = row["coordinates"]
        order = int(row["order"])
        # If coordinates are provided, generate images at 4 headings
        if location is not None:
            lst_valid_url = [] 
            for heading in [0, 90, 180, 270]:
                request_url = get_street_view_image(group_name=group_name, location=location, heading=heading, order=order)
                if request_url:  
                    filtered_df.at[i, f"request_url_heading_{heading}"] = request_url # url from the GSV
                    my_payload = {
                                "url":request_url,
                                "location": f"({location[0]},{location[1]})",  
                                "heading":heading,
                                "order":order,
                                "group":group_name
                            }

                    print(my_payload)
                    
                    invoke_lambda(
                            my_payload=my_payload, 
                            lambda_name=config.lambda_1_label_img, 
                            invocation_type="Event"
                            )

    return filtered_df

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
# Initialize DynamoDB resource

region_name="us-east-1"
dynamodb = boto3.resource('dynamodb',region_name=region_name)
s3_client = boto3.client("s3")

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
    

def get_street_view_image(
    group_name,
    location,
    heading,
    pitch=0,
    fov=config.gsv_fov,
    order=None,
    local_name=None,
    bucket_name="gov-sananga",
    s3_key="",
    verbose=False
):
    """
    Fetches a Google Street View image for the given location and heading,
    validates it, and uploads it to S3 if valid.

    Parameters:
    - group_name: name of the group (used in folder structure)
    - location: tuple (lat, lng)
    - heading: camera direction in degrees
    - pitch: camera tilt (default 0)
    - fov: field of view (default from config)
    - order: image order/index in group
    - local_name: normalized place name (used as top-level S3 prefix)
    - bucket_name: S3 bucket to upload image to
    - verbose: enable debug output

    Returns:
    - request_url if image uploaded to S3
    - False if no valid image found
    """
    import requests
    from PIL import Image
    from io import BytesIO
    import boto3

    assert local_name, "local_name is required to construct S3 key"

    # Build Google Street View request
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": "2048x2048",
        "location": f"{location[0]},{location[1]}",
        "heading": heading,
        "pitch": pitch,
        "fov": fov,
        "key": gcp_api_key,
    }
    request_url = requests.Request('GET', base_url, params=params).prepare().url

    # Fetch image
    response = requests.get(base_url, params=params)
    if response.status_code != 200 or not response.content:
        if verbose:
            print(f"[FAIL] {response.status_code} - No image content")
        return False

    try:
        image = Image.open(BytesIO(response.content))

        if image.getbbox() and is_image_valid(image):
            # Upload to S3
            s3 = boto3.client("s3")
            s3.upload_fileobj(BytesIO(response.content), bucket_name, s3_key, ExtraArgs={"ContentType": "image/jpeg"})

            if verbose:
                print(f"[SUCCESS] Uploaded to s3://{bucket_name}/{s3_key}")
            return request_url
        else:
            if verbose:
                print("[INFO] Image is blank or invalid.")
            return False

    except Exception as e:
        if verbose:
            print(f"[ERROR] Failed to process image: {e}")
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



def upload_to_s3(image_content, s3_key):
    s3_client.upload_fileobj(BytesIO(image_content), bucket_name, s3_key)
    # Generate pre-signed URL valid for 1 hour
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": s3_key},
        ExpiresIn=3600
    )

def automate_street_view_images(df, group_name, bucket_name, region, verbose=False):
    import boto3
    from io import BytesIO

    filtered_df = df[df["group"] == group_name].reset_index(drop=True)

    if verbose:
        print(f"[INFO] Processing group: {group_name} with {len(filtered_df)} rows")

    filtered_df["s3_path"] = None

    for i, row in filtered_df.iterrows():
        location = row["coordinates"]
        place = row["place"]
        order = int(row["order"])

        if location is not None:
            for heading in [0, 90, 180, 270]:
                # Fetch image and upload directly to S3 (returns request URL if successful)
                s3_key = f"{place}/google_street_view/group-{group_name}/order-{order}-heading-{heading}.jpg"
                request_url = get_street_view_image(
                    group_name=group_name,
                    location=location,
                    heading=heading,
                    order=order,
                    local_name=place,
                    bucket_name=bucket_name,
                    s3_key=s3_key,
                    verbose=verbose
                )

                if request_url:
                    # Save S3 info in DataFrame
                    filtered_df.at[i, "s3_path"] = s3_key
                    s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
                    filtered_df.at[i, f"request_url_heading_{heading}"] = s3_url

                    # Lambda payload
                    payload = {
                        "bucket": bucket_name,
                        "key": s3_key,
                        "place": place,
                        "location": f"({location[0]},{location[1]})",
                        "heading": heading,
                        "order": order,
                        "group": group_name,
                        "s3_link": s3_url
                    }

                    if verbose:
                        print(f"[LAMBDA PAYLOAD] {payload}")

                    # Invoke Lambda asynchronously
                    invoke_lambda(
                        my_payload=payload,
                        lambda_name=config.lambda_1_label_img,
                        invocation_type="Event"
                    )
                elif verbose:
                    print(f"[SKIPPED] No valid image for heading {heading} at {location}")

    return filtered_df


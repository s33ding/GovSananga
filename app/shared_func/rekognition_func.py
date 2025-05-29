import boto3
import requests
from io import BytesIO

region_name="us-east-1"

def analyze_image(image_url):
    # Initialize the Rekognition client
    client = boto3.client('rekognition', region_name=region_name)

    # Download the image from the provided URL
    response = requests.get(image_url)
    image_bytes = BytesIO(response.content)

    # Use Rekognition to detect text in the image
    rekognition_response = client.detect_text(
        Image={'Bytes': image_bytes.read()}
    )

    # Extract detected text from Rekognition response
    detected_text = []
    for text in rekognition_response['TextDetections']:
        if text['Type'] == 'LINE':  # Extract full lines of text
            detected_text.append(text['DetectedText'])

    # Return the detected text
    return rekognition_response 

def check_for_store_in_image(image_url):
    # Initialize Rekognition client
    client = boto3.client('rekognition', region_name=region_name)

    # Download the image from the provided URL
    response = requests.get(image_url)
    image_bytes = BytesIO(response.content)

    # Call Rekognition to detect labels in the image
    rekognition_response = client.detect_labels(
        Image={'Bytes': image_bytes.read()},
        MaxLabels=10,  # Limit the number of labels
        MinConfidence=70  # Set a minimum confidence level
    )

    # Check for relevant labels that could indicate a store
    store_related_labels = ['Building', 'Shop', 'Sign', 'Retail', 'Storefront']
    detected_labels = [label['Name'] for label in rekognition_response['Labels']]

    # Determine if any store-related labels are found
    is_store_detected = any(label in store_related_labels for label in detected_labels)

    return is_store_detected, detected_labels

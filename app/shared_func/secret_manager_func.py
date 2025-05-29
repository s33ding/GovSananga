import boto3
import json
from app.config import region_name

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb',region_name=region_name)

def get_secret(secret_name):
    """
    Retrieves the value of the specified AWS Secrets Manager secret using the provided session object
    
    Args:
    - secret_name (str): the name of the AWS Secrets Manager secret to retrieve
    - session (boto3.Session): the session object for initializing the Secrets Manager client
    
    Returns:
    - dct (dict): a dictionary containing the values in the specified secret
    """
    # Initialize the Secrets Manager client using the session
    client = boto3.client('secretsmanager', region_name=region_name)
    
    # Use Secrets Manager client object to get secret value
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    
    # Extract the values from the secret
    dct = json.loads(get_secret_value_response['SecretString'])
    
    return dct

def list_secrets(region_name=region_name, verbose=True):
    """
    List secrets in AWS Secrets Manager.

    Args:
    region_name (str): AWS region where the secrets manager is located. Default is 'us-east-1'.

    Returns:
    list: List of secret names.
    """
    # Initialize the Secrets Manager client
    client = boto3.client('secretsmanager', region_name=region_name)

    # Call the list_secrets API
    response = client.list_secrets()

    # Extract secret names from the response
    secret_names = [secret['Name'] for secret in response['SecretList']]
    if verbose:
        for v in secret_names:
            print(v)

    return secret_names

def create_secret(secret_name, secret_value_json, region_name=region_name):
    """
    Create a new secret in AWS Secrets Manager.

    Args:
    secret_name (str): Name for the new secret.
    secret_value_json (dict): JSON object containing the value for the new secret.
    region_name (str): AWS region where the secrets manager is located. Default is 'us-east-1'.

    Returns:
    dict: Response from the Secrets Manager API.
    """
    # Convert the JSON object to a string
    secret_value_str = json.dumps(secret_value_json)

    # Initialize the Secrets Manager client
    client = boto3.client('secretsmanager', region_name=region_name)

    # Call the create_secret API
    response = client.create_secret(
        Name=secret_name,
        SecretString=secret_value_str
    )

    return response

def delete_secret(secret_name, region_name=region_name):
    """
    Delete a secret from AWS Secrets Manager.

    Args:
    secret_name (str): Name of the secret to delete.
    region_name (str): AWS region where the secrets manager is located. Default is 'us-east-1'.

    Returns:
    dict: Response from the Secrets Manager API.
    """
    # Initialize the Secrets Manager client
    client = boto3.client('secretsmanager', region_name=region_name)

    # Call the delete_secret API
    response = client.delete_secret(
        SecretId=secret_name,
        ForceDeleteWithoutRecovery=True  # Set to True to delete the secret immediately without recovery
    )

    return response

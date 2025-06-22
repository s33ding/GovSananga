import boto3
import json

# Function to invoke another Lambda function
def invoke_lambda(my_payload, lambda_name, invocation_type):
  client = boto3.client("lambda")
  print(my_payload)
  response = client.invoke(
      FunctionName = lambda_name,
      InvocationType = invocation_type, # best options: RequestResponse or Event
      Payload = json.dumps(my_payload))
  return response
  
def extract_response_value(lambda_response):
    payload_bytes = lambda_response['Payload'].read()
    payload_str = payload_bytes.decode('utf-8')
    payload_obj = json.loads(payload_str)
    return payload_obj["body"]

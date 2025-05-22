from shared_func.secret_manager_func import get_secret
import openai
from openai import OpenAI

# Fetch the API key once and reuse it
openai_api_key =  get_secret("s33ding").get("openai")

def analyze_image_with_prompt(image_url, prompt):

    # Initialize the OpenAI client
    client = OpenAI(api_key = openai_api_key)

    # Make the request with a prompt and image URL
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }
        ],
        max_tokens=300
    )

    # Extract and return the response content
    return response.choices[0]

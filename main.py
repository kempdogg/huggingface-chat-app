import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('HUGGINGFACE_API_KEY')
API_URL = 'https://router.huggingface.co'

# Example function to call the Hugging Face Inference API 
def call_inference_api(data):
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()
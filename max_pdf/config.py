import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_api_key():
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    return key
import os
from dotenv import load_dotenv
from pathlib import Path

# / operator does OS agnostic path extension from Path lib
home_config = Path.home() / ".max_config.env"
if home_config.exists():
    load_dotenv(home_config)

# Load environment variables
load_dotenv()

def get_api_key():
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "\n[Error] Missing GOOGLE_API_KEY.\n\n"
            "To use Max globally, please do EITHER:\n"
            "1. Export the key in your shell profile (~/.zshrc or ~/.bashrc):\n"
            "   export GOOGLE_API_KEY='your_key_here'\n\n"
            "2. OR Create a config file at ~/.max_config.env with the line:\n"
            "   GOOGLE_API_KEY=your_key_here"
        )
    return key
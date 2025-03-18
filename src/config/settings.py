import os
from typing import Dict, Any
from dotenv import load_dotenv

def debug_print(class_name: str, function_name: str, detail: str):
    print(f"[settings][{class_name}][{function_name}] {detail}")

class Settings:
    def __init__(self):
        load_dotenv()
        debug_print("Settings", "__init__", "Loading environment variables")
        
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
            
        self.azure_openai = {
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.getenv("AZURE_OPENAI_KEY"),
            "model_name": os.getenv("MODEL_NAME"),
            "api_version": os.getenv("API_VERSION")
        }
        debug_print("Settings", "__init__", "Initialized with all settings")

    def get_azure_openai_config(self) -> Dict[str, Any]:
        """Get Azure OpenAI configuration."""
        return self.azure_openai

    def get_telegram_token(self) -> str:
        """Get Telegram bot token."""
        return self.telegram_token

settings = Settings()

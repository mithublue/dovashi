import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load backend/.env explicitly so running from repo root works
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


@dataclass
class Settings:
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    tts_model_name: str = os.getenv("TTS_MODEL_NAME", "tts_models/multilingual/multi-dataset/xtts_v2")
    cors_allow_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()

from __future__ import annotations
import os
from typing import Optional

import google.generativeai as genai

from .base import ASRTranslateProvider


class GeminiProvider(ASRTranslateProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        genai.configure(api_key=key)
        self.model_name = model
        self.model = genai.GenerativeModel(self.model_name)

    def transcribe(self, audio_path: str, source_lang: Optional[str] = None) -> str:
        prompt = (
            "Transcribe the speech from the audio exactly and accurately. "
            "Return plain text only without timestamps or extra commentary."
        )
        if source_lang:
            prompt += f" The speech language is '{source_lang}'."

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        audio_part = {"mime_type": "audio/wav", "data": audio_bytes}
        try:
            res = self.model.generate_content([prompt, audio_part])
            return (res.text or "").strip()
        except Exception as e:
            raise RuntimeError(f"Gemini transcription failed: {e}")

    def translate(self, text: str, target_lang: str) -> str:
        if not text.strip():
            return ""
        prompt = (
            "Translate the following text into the target language specified. "
            "Return only the translated text, with no extra commentary.\n\n"
            f"Target language code or name: {target_lang}\n"
            f"Text: {text}"
        )
        try:
            res = self.model.generate_content(prompt)
            return (res.text or "").strip()
        except Exception as e:
            raise RuntimeError(f"Gemini translation failed: {e}")

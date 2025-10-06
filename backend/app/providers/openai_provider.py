from __future__ import annotations
import os
from typing import Optional

from openai import OpenAI

from .base import ASRTranslateProvider


class OpenAIProvider(ASRTranslateProvider):
    def __init__(self, api_key: Optional[str] = None, chat_model: Optional[str] = None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=key)
        self.chat_model = chat_model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        self.whisper_model = os.getenv("OPENAI_WHISPER_MODEL", "whisper-1")

    def transcribe(self, audio_path: str, source_lang: Optional[str] = None) -> str:
        # Whisper ignores source_lang; it autodetects. We pass file directly.
        with open(audio_path, "rb") as f:
            try:
                res = self.client.audio.transcriptions.create(model=self.whisper_model, file=f)
                # SDK returns an object with .text
                return (res.text or "").strip()
            except Exception as e:
                raise RuntimeError(f"OpenAI Whisper transcription failed: {e}")

    def translate(self, text: str, target_lang: str) -> str:
        if not text.strip():
            return ""
        system = (
            "You are a high-quality translator. Translate the user's text to the target language. "
            "Return ONLY the translated text with no explanations."
        )
        user = f"Target language: {target_lang}\nText: {text}"
        try:
            res = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            )
            return (res.choices[0].message.content or "").strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI translation failed: {e}")

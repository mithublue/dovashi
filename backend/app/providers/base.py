from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class ASRTranslateProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, source_lang: Optional[str] = None) -> str:
        """Transcribe speech to text. Should return plain text only."""
        raise NotImplementedError

    @abstractmethod
    def translate(self, text: str, target_lang: str) -> str:
        """Translate text to target language code. Return plain text only."""
        raise NotImplementedError

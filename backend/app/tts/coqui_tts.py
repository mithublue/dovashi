from __future__ import annotations
import threading
from typing import Optional, Tuple

import numpy as np

from TTS.api import TTS


class CoquiTTS:
    """
    Lazy-initialized Coqui TTS (XTTS v2) synthesizer.
    Usage:
        wav, sr = CoquiTTS().synthesize(text, language="en", speaker_wav=None)
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, model_name: str | None = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_model(model_name)
        return cls._instance

    def _init_model(self, model_name: Optional[str] = None):
        self.model_name = model_name or "tts_models/multilingual/multi-dataset/xtts_v2"
        # TTS will automatically use CUDA if available
        self.tts = TTS(model_name=self.model_name)
        # Access the output sample rate from synthesizer
        try:
            self.sample_rate = getattr(self.tts.synthesizer, "output_sample_rate", 24000)
        except Exception:
            self.sample_rate = 24000

    def synthesize(self, text: str, language: str = "en", speaker_wav: Optional[str] = None) -> Tuple[np.ndarray, int]:
        if not text.strip():
            return np.zeros(1, dtype=np.float32), self.sample_rate
        # Prefer explicit language and optional speaker_wav for XTTS
        wav = self.tts.tts(text=text, language=language, speaker_wav=speaker_wav)
        # Ensure float32 numpy array
        wav = np.asarray(wav, dtype=np.float32)
        return wav, self.sample_rate

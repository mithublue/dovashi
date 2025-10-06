from __future__ import annotations
import os
import tempfile
from typing import Literal, Optional, List, Dict

import numpy as np
import soundfile as sf

from .utils.audio import (
    ensure_wav,
    load_mono_wav,
    segment_audio_vad,
    save_chunk_to_wav,
    assemble_with_pauses,
)
from .providers.gemini_provider import GeminiProvider
from .providers.openai_provider import OpenAIProvider
from .tts.coqui_tts import CoquiTTS


ProviderName = Literal["gemini", "openai"]


def _get_provider(name: ProviderName):
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown provider: {name}")


def _prepare_audio(
    input_path: str,
    target_lang: str,
    provider: ProviderName,
    source_lang: Optional[str],
    vad_top_db: float,
    vad_min_gap_s: float,
) -> Dict[str, object]:
    std_wav = ensure_wav(input_path, target_sr=16000)
    y, sr = load_mono_wav(std_wav, sr=16000)
    segments, gaps = segment_audio_vad(y, sr, top_db=vad_top_db, min_gap_s=vad_min_gap_s)

    prov = _get_provider(provider)
    transcripts: List[str] = []
    translations: List[str] = []

    for (s, e) in segments:
        seg = y[s:e]
        seg_path = save_chunk_to_wav(seg, sr)
        try:
            transcript = prov.transcribe(seg_path, source_lang=source_lang)
        finally:
            try:
                os.remove(seg_path)
            except Exception:
                pass
        transcripts.append(transcript)

        if target_lang and target_lang.strip():
            try:
                translated = prov.translate(transcript, target_lang)
            except Exception:
                translated = transcript
        else:
            translated = transcript
        translations.append(translated)

    return {
        "std_wav": std_wav,
        "wave": y,
        "sample_rate": sr,
        "segments": segments,
        "gaps": gaps,
        "transcripts": transcripts,
        "translations": translations,
    }


def convert_audio(
    input_path: str,
    target_lang: str,
    provider: ProviderName = "gemini",
    source_lang: Optional[str] = None,
    vad_top_db: float = 30.0,
    vad_min_gap_s: float = 0.25,
    tts_speaker_wav: Optional[str] = None,
) -> str:
    """
    Convert speech audio to target language while preserving pauses.
    Returns a path to a temporary WAV file containing the synthesized speech.
    """
    prep = _prepare_audio(
        input_path=input_path,
        target_lang=target_lang,
        provider=provider,
        source_lang=source_lang,
        vad_top_db=vad_top_db,
        vad_min_gap_s=vad_min_gap_s,
    )

    try:
        translations: List[str] = prep["translations"]  # type: ignore[assignment]
        gaps: List[float] = prep["gaps"]  # type: ignore[assignment]

        tts = CoquiTTS()
        seg_audios: list[np.ndarray] = []
        seg_srs: list[int] = []

        for translated in translations:
            try:
                wav, wav_sr = tts.synthesize(translated, language=target_lang or "en", speaker_wav=tts_speaker_wav)
            except Exception:
                try:
                    wav, wav_sr = tts.synthesize(translated, language="en", speaker_wav=tts_speaker_wav)
                except Exception:
                    wav = np.zeros(int(0.2 * 24000), dtype=np.float32)
                    wav_sr = 24000
            seg_audios.append(wav)
            seg_srs.append(wav_sr)

        if seg_audios:
            chosen_sr = max(set(seg_srs), key=seg_srs.count) if seg_srs else 24000
            final = assemble_with_pauses(seg_audios, seg_srs, gaps_seconds=gaps, target_sr=chosen_sr)
        else:
            final = np.zeros(1, dtype=np.float32)
            chosen_sr = 24000

        out_sr = chosen_sr

        fd, out_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        sf.write(out_path, final, out_sr, subtype="PCM_16")
        return out_path
    finally:
        std_wav: str = prep["std_wav"]  # type: ignore[assignment]
        try:
            os.remove(std_wav)
        except Exception:
            pass


def convert_audio_to_text(
    input_path: str,
    target_lang: str,
    provider: ProviderName = "gemini",
    source_lang: Optional[str] = None,
    vad_top_db: float = 30.0,
    vad_min_gap_s: float = 0.25,
) -> Dict[str, object]:
    prep = _prepare_audio(
        input_path=input_path,
        target_lang=target_lang,
        provider=provider,
        source_lang=source_lang,
        vad_top_db=vad_top_db,
        vad_min_gap_s=vad_min_gap_s,
    )

    try:
        transcripts: List[str] = prep["transcripts"]  # type: ignore[assignment]
        translations: List[str] = prep["translations"]  # type: ignore[assignment]

        translation_text = " ".join(t.strip() for t in translations if t and t.strip()).strip()
        transcript_text = " ".join(t.strip() for t in transcripts if t and t.strip()).strip()

        if not translation_text:
            translation_text = transcript_text

        segments_payload = [
            {
                "transcript": transcripts[i],
                "translation": translations[i],
            }
            for i in range(len(translations))
        ]

        return {
            "translation": translation_text or "",
            "transcript": transcript_text or "",
            "segments": segments_payload,
        }
    finally:
        std_wav: str = prep["std_wav"]  # type: ignore[assignment]
        try:
            os.remove(std_wav)
        except Exception:
            pass

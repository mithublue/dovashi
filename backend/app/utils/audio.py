import os
import tempfile
import mimetypes
from typing import List, Tuple, Dict

import numpy as np
import librosa
import soundfile as sf
import ffmpeg


def ensure_wav(input_path: str, target_sr: int = 16000) -> str:
    """
    Ensure the input audio is a WAV PCM 16-bit mono at target_sr. If not, convert via ffmpeg.
    Returns the path to a temporary WAV file (may be the original if already compliant).
    """
    try:
        y, sr = librosa.load(input_path, sr=None, mono=True)
        # Re-write to temporary standardized wav
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        os.close(tmp_fd)
        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
            sr = target_sr
        sf.write(tmp_path, y, sr, subtype="PCM_16")
        return tmp_path
    except Exception:
        # Fallback: use ffmpeg to convert any format to wav
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        os.close(tmp_fd)
        (
            ffmpeg
            .input(input_path)
            .output(tmp_path, ac=1, ar=target_sr, f='wav', acodec='pcm_s16le')
            .overwrite_output()
            .run(quiet=True)
        )
        return tmp_path


def load_mono_wav(path: str, sr: int = 16000) -> Tuple[np.ndarray, int]:
    y, s = librosa.load(path, sr=sr, mono=True)
    return y, s


def segment_audio_vad(y: np.ndarray, sr: int, top_db: float = 30.0, min_gap_s: float = 0.25) -> Tuple[List[Tuple[int, int]], List[float]]:
    """
    Segment audio into voiced chunks using an energy-based splitter.
    Returns:
    - segments: list of (start_sample, end_sample)
    - gaps_seconds: list of gaps between segments including leading and trailing silences.
      Length is len(segments) + 1: [leading_silence, gap1, gap2, ..., trailing_silence]
    """
    intervals = librosa.effects.split(y, top_db=top_db)
    if len(intervals) == 0:
        # Treat whole audio as one segment
        intervals = np.array([[0, len(y)]])

    # Merge segments that are separated by very small gaps (< min_gap_s)
    merged = []
    for start, end in intervals:
        if not merged:
            merged.append([int(start), int(end)])
        else:
            prev_start, prev_end = merged[-1]
            gap = (start - prev_end) / sr
            if gap < min_gap_s:
                merged[-1][1] = int(end)
            else:
                merged.append([int(start), int(end)])

    segments = [(s, e) for s, e in merged]

    # Compute gaps (leading, betweens, trailing)
    gaps_seconds: List[float] = []
    # Leading
    leading = segments[0][0] / sr
    gaps_seconds.append(max(0.0, float(leading)))
    # Between
    for i in range(len(segments) - 1):
        gap = (segments[i + 1][0] - segments[i][1]) / sr
        gaps_seconds.append(max(0.0, float(gap)))
    # Trailing
    trailing = (len(y) - segments[-1][1]) / sr
    gaps_seconds.append(max(0.0, float(trailing)))

    return segments, gaps_seconds


def save_chunk_to_wav(y: np.ndarray, sr: int) -> str:
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    sf.write(path, y, sr, subtype="PCM_16")
    return path


def assemble_with_pauses(segment_audios: List[np.ndarray], segment_srs: List[int], gaps_seconds: List[float], target_sr: int = 22050) -> np.ndarray:
    """
    Interleave gaps (silence) and segment audios preserving original pauses.
    gaps_seconds length must be len(segment_audios) + 1
    """
    assert len(gaps_seconds) == len(segment_audios) + 1

    # Resample all segments to target_sr
    segments_resampled = [
        librosa.resample(seg, orig_sr=sr, target_sr=target_sr) if sr != target_sr else seg
        for seg, sr in zip(segment_audios, segment_srs)
    ]

    output = []
    # Leading silence
    if gaps_seconds[0] > 0:
        output.append(np.zeros(int(target_sr * gaps_seconds[0]), dtype=np.float32))

    for i, seg in enumerate(segments_resampled):
        output.append(seg.astype(np.float32))
        gap = gaps_seconds[i + 1]
        if gap > 0:
            output.append(np.zeros(int(target_sr * gap), dtype=np.float32))

    if output:
        return np.concatenate(output)
    else:
        return np.zeros(1, dtype=np.float32)


def guess_mime_type(path: str) -> str:
    mt, _ = mimetypes.guess_type(path)
    return mt or 'application/octet-stream'

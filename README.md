# Dovashi

Multilingual speech-to-speech and speech-to-text assistant powered by Gemini 2.5 Flash (default) or OpenAI Whisper + GPT. The app preserves pauses, supports on-device playback/download, and exposes a text-only conversion workflow.

## Features
* __Dual providers__: Switch between `Gemini` and `OpenAI` for transcription and translation.
* __Pause preservation__: Voice Activity Detection (VAD) segments speech and rebuilds output audio with original gaps.
* __Text conversion__: Convert uploaded or recorded audio to translated text with per-segment transcripts.
* __Modern UI__: Vite + React + Tailwind front-end inspired by Perplexity.
* __Downloadable results__: Preview and download the converted audio as WAV.

## Project Structure
```
dovashi/
├── backend/              # FastAPI service
│   ├── app/
│   │   ├── main.py       # API endpoints
│   │   ├── pipeline.py   # Conversion pipeline
│   │   └── providers/    # Gemini & OpenAI integrations
│   └── requirements.txt
├── frontend/             # Vite + React client
│   ├── src/App.tsx
│   └── package.json
├── .gitignore
└── README.md
```

## Requirements
* Python 3.10 or 3.11 (recommended 64-bit)
* Node.js 18+
* FFmpeg available on PATH (audio decoding)
* Microsoft C++ Build Tools with Windows 10/11 SDK (required for `TTS` wheel build on Windows)
* PyTorch (CPU or CUDA) – install after backend requirements

## Environment Variables
Create `backend/.env` (copy from `backend/.env.example` if provided):
```
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key   # optional unless using OpenAI provider
FRONTEND_ORIGIN=http://localhost:5173
TTS_MODEL_NAME=tts_models/multilingual/multi-dataset/xtts_v2
```
For the frontend, define `frontend/.env` or `.env.local`:
```
VITE_API_BASE=http://localhost:8000
```

## Setup
### 1. Clone & create virtual environment
```powershell
git clone <repo>
cd dovashi
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install backend dependencies
```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r backend/requirements.txt
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```
> For GPU builds, replace the CPU wheel URL with the appropriate CUDA wheel.

### 3. Install Node dependencies
```powershell
cd frontend
npm install
cd ..
```

### 4. Ensure FFmpeg is installed
* Chocolatey: `choco install ffmpeg`
* Manual: download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/), unzip, add `bin` folder to PATH.

## Running Locally
### Start the backend
```powershell
.\.venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
```

### Start the frontend
```powershell
cd frontend
npm run dev
```

Visit `http://localhost:5173`.

## Usage
1. Record audio or upload a file (wav, mp3, m4a, webm, etc.).
2. Choose target language and optional source language; switch provider if desired.
3. Click **Convert to speech** to receive a pause-preserving translated WAV.
4. Click **Convert to text** to receive translated text plus original transcript and per-segment details.
5. Download audio output or copy text as needed.

## API Endpoints
* `GET /api/health` – health check
* `GET /api/providers` – available providers
* `POST /api/convert` – multipart form (`file`, `target_lang`, optional `provider`, `source_lang`), returns WAV
* `POST /api/convert-text` – same payload, returns JSON `{ translation, transcript, segments[] }`

## Troubleshooting
* __Gemini key missing__: ensure `backend/.env` is loaded and restart `uvicorn`.
* __soundfile / TTS build errors__: confirm MSVC build tools + Windows SDK and run pip install again.
* __PyTorch missing__: install wheel suitable for your hardware.
* __FFmpeg errors__: install FFmpeg and restart shell so PATH updates.
* __Missing punctuation__: use the text conversion endpoint in the Gemini web UI if stricter formatting is essential; the app uses chunked VAD segments which may slightly differ from a single-shot transcription.

## License
Specify your license here (MIT, Apache 2.0, etc.)

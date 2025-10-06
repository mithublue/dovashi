from __future__ import annotations
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask

from .config import settings
from .pipeline import convert_audio, convert_audio_to_text

app = FastAPI(title="Dovashi Speech-to-Speech", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_allow_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/providers")
def providers():
    return {"providers": ["gemini", "openai"]}


@app.post("/api/convert")
async def api_convert(
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    provider: str = Form("gemini"),
    source_lang: Optional[str] = Form(None),
):
    if provider not in ("gemini", "openai"):
        raise HTTPException(status_code=400, detail="provider must be 'gemini' or 'openai'")

    # Save uploaded file to temp
    try:
        fd, tmp_in = tempfile.mkstemp(suffix=os.path.splitext(file.filename or "uploaded")[1] or ".wav")
        with os.fdopen(fd, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

    try:
        out_path = convert_audio(
            input_path=tmp_in,
            target_lang=target_lang,
            provider=provider,  # type: ignore
            source_lang=source_lang,
        )
    except Exception as e:
        # Clean input tmp
        try:
            os.remove(tmp_in)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))

    # Delete both input and output once sent
    def cleanup():
        for p in (tmp_in, out_path):
            try:
                os.remove(p)
            except Exception:
                pass

    headers = {
        "Content-Disposition": f"attachment; filename=converted.wav"
    }
    return FileResponse(out_path, media_type="audio/wav", headers=headers, background=BackgroundTask(cleanup))


@app.post("/api/convert-text")
async def api_convert_text(
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    provider: str = Form("gemini"),
    source_lang: Optional[str] = Form(None),
):
    if provider not in ("gemini", "openai"):
        raise HTTPException(status_code=400, detail="provider must be 'gemini' or 'openai'")

    try:
        fd, tmp_in = tempfile.mkstemp(suffix=os.path.splitext(file.filename or "uploaded")[1] or ".wav")
        with os.fdopen(fd, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

    try:
        result = convert_audio_to_text(
            input_path=tmp_in,
            target_lang=target_lang,
            provider=provider,  # type: ignore
            source_lang=source_lang,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.remove(tmp_in)
        except Exception:
            pass

    return result


@app.get("/")
def root():
    return JSONResponse({
        "name": "Dovashi Speech-to-Speech API",
        "endpoints": {
            "health": "/api/health",
            "providers": "/api/providers",
            "convert": "POST /api/convert (multipart/form-data)",
            "convert-text": "POST /api/convert-text (multipart/form-data)"
        }
    })

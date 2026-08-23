import os
import shutil
import zipfile
import tempfile
import uuid
import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from utils import check_ffmpeg, sanitize_filename
from downloader import download_audio
from transcript_parser import (
    extract_video_id,
    get_cuts_from_transcript,
    get_cuts_from_video_info,
    parse_manual_tracklist
)
from splitter import split_and_export

app = FastAPI(title="YouTube Audio Splitter API (Ephemeral Storage)")

# Enable CORS for React UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://youtube-audio-splitter.johnathikalam3.workers.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_TEMP_DIR = os.path.join(tempfile.gettempdir(), "yt_splitter_sessions")
os.makedirs(BASE_TEMP_DIR, exist_ok=True)

class SplitRequest(BaseModel):
    url: str
    tracklist: str = ""

def purge_old_sessions(max_age_seconds: int = 600):
    """Deletes temporary session directories older than max_age_seconds."""
    now = time.time()
    if not os.path.exists(BASE_TEMP_DIR):
        return
    for item in os.listdir(BASE_TEMP_DIR):
        item_path = os.path.join(BASE_TEMP_DIR, item)
        if os.path.isdir(item_path):
            try:
                mtime = os.path.getmtime(item_path)
                if (now - mtime) > max_age_seconds:
                    shutil.rmtree(item_path, ignore_errors=True)
            except Exception:
                pass

def delete_directory(dir_path: str):
    """Background task callback to delete a session directory after serving files."""
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)

@app.on_event("startup")
def startup_event():
    check_ffmpeg()
    purge_old_sessions(max_age_seconds=0)  # Clean lingering session files from previous runs

@app.get("/api/health")
def health_check():
    return {"status": "ok", "ffmpeg": shutil.which("ffmpeg") is not None}

@app.post("/api/split")
def split_audio(req: SplitRequest, background_tasks: BackgroundTasks):
    # Purge any expired temporary sessions
    background_tasks.add_task(purge_old_sessions)

    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="YouTube URL is required.")

    try:
        video_id = extract_video_id(url)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    cuts = []

    # 1. Parse manual tracklist if provided
    if req.tracklist.strip():
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as tf:
            tf.write(req.tracklist)
            tf_path = tf.name
        try:
            cuts = parse_manual_tracklist(tf_path)
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)

    # 2. Fallback to transcript
    if not cuts:
        cuts = get_cuts_from_transcript(video_id)

    session_id = uuid.uuid4().hex
    session_dir = os.path.join(BASE_TEMP_DIR, session_id)
    tracks_dir = os.path.join(session_dir, "tracks")
    temp_download_dir = os.path.join(session_dir, "dl_temp")
    os.makedirs(tracks_dir, exist_ok=True)
    os.makedirs(temp_download_dir, exist_ok=True)

    try:
        # 3. Download audio stream
        audio_file, video_title, video_info = download_audio(url, temp_dir=temp_download_dir)

        # 4. Fallback to chapters/description if still no cuts
        if not cuts:
            cuts = get_cuts_from_video_info(video_info)

        if not cuts:
            shutil.rmtree(session_dir, ignore_errors=True)
            raise HTTPException(
                status_code=422,
                detail="No split points found via transcript, chapters, or manual tracklist. Please enter a tracklist."
            )

        # 5. Split tracks into session temporary folder
        split_and_export(audio_file, cuts, tracks_dir)

        # Clean raw downloaded stream file to free memory/disk immediately
        if os.path.exists(temp_download_dir):
            shutil.rmtree(temp_download_dir, ignore_errors=True)

        clean_folder_name = sanitize_filename(video_title)
        zip_filename = f"{clean_folder_name}.zip"
        zip_filepath = os.path.join(session_dir, zip_filename)
        
        # 6. Build ZIP archive of exported tracks inside session temp dir
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(tracks_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, tracks_dir)
                    zipf.write(file_path, arcname)

        # Build exported track list metadata
        exported_files = sorted([f for f in os.listdir(tracks_dir) if f.endswith(".mp3")])
        tracks_meta = []
        for i, fname in enumerate(exported_files):
            fpath = os.path.join(tracks_dir, fname)
            size_mb = os.path.getsize(fpath) / (1024 * 1024)
            tracks_meta.append({
                "index": i + 1,
                "filename": fname,
                "size_mb": round(size_mb, 2),
                "download_url": f"/api/download_track/{session_id}/{fname}"
            })

        return {
            "status": "success",
            "video_title": video_title,
            "session_id": session_id,
            "total_tracks": len(tracks_meta),
            "download_zip": f"/api/download_zip/{session_id}",
            "tracks": tracks_meta
        }

    except HTTPException:
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir, ignore_errors=True)
        raise
    except Exception as e:
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Failed to process YouTube audio: {str(e)}")

@app.get("/api/download_zip/{session_id}")
def download_zip(session_id: str, background_tasks: BackgroundTasks):
    safe_session = os.path.basename(session_id)
    session_dir = os.path.join(BASE_TEMP_DIR, safe_session)
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Requested download session has expired or does not exist.")

    zip_files = [f for f in os.listdir(session_dir) if f.endswith(".zip")]
    if not zip_files:
        raise HTTPException(status_code=404, detail="Zip file not found.")

    zip_path = os.path.join(session_dir, zip_files[0])
    
    # Schedule session cleanup after client finishes downloading the zip
    background_tasks.add_task(delete_directory, session_dir)

    return FileResponse(zip_path, media_type="application/zip", filename=zip_files[0])

@app.get("/api/download_track/{session_id}/{filename}")
def download_individual_track(session_id: str, filename: str):
    safe_session = os.path.basename(session_id)
    safe_file = os.path.basename(filename)
    file_path = os.path.join(BASE_TEMP_DIR, safe_session, "tracks", safe_file)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested track file has expired or does not exist.")
    
    return FileResponse(file_path, media_type="audio/mpeg", filename=safe_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))

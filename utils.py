import os
import re
import shutil
import sys

def check_ffmpeg():
    """Verify that ffmpeg is available in system PATH, attempting PATH refresh or static-ffmpeg fallback."""
    if shutil.which("ffmpeg"):
        return
    
    # Try refreshing PATH from Windows Registry if on Windows
    if sys.platform.startswith("win"):
        user_path = os.environ.get("PATH", "")
        reg_path = os.popen('powershell -Command "[System.Environment]::GetEnvironmentVariable(\'Path\',\'User\') + \';\' + [System.Environment]::GetEnvironmentVariable(\'Path\',\'Machine\')"').read().strip()
        if reg_path:
            os.environ["PATH"] = reg_path
            if shutil.which("ffmpeg"):
                return

    # Fallback to static_ffmpeg if installed
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
        if shutil.which("ffmpeg"):
            return
    except Exception:
        pass

    print("Error: 'ffmpeg' is not found in system PATH. Please install FFmpeg to process audio.")
    sys.exit(1)

def sanitize_filename(name: str) -> str:
    """Remove invalid filesystem characters from folder/file names."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = re.sub(r'\s+', "_", cleaned.strip())
    return cleaned if cleaned else "unnamed_track"

def timecode_to_ms(timecode: str) -> int:
    """Convert timecode formats (HH:MM:SS, MM:SS, or seconds) to milliseconds."""
    clean_tc = timecode.strip().replace(",", ".")
    parts = clean_tc.split(":")
    try:
        if len(parts) == 3:
            h, m, s = map(float, parts)
            return int((h * 3600 + m * 60 + s) * 1000)
        elif len(parts) == 2:
            m, s = map(float, parts)
            return int((m * 60 + s) * 1000)
        elif len(parts) == 1:
            return int(float(parts[0]) * 1000)
    except ValueError:
        pass
    raise ValueError(f"Invalid timestamp format: '{timecode}'")
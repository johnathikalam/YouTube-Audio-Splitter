import os
import yt_dlp
from utils import sanitize_filename

def download_audio(url: str, temp_dir: str = "temp") -> tuple[str, str, dict]:
    """
    Downloads best audio from YouTube URL as MP3.
    Returns tuple: (file_path, sanitized_video_title, video_info_dict)
    """
    os.makedirs(temp_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'tv_embedded']
            }
        },
        # Uses cookies.txt if uploaded to your Colab directory
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get('id')
        raw_title = info.get('title', 'Unknown_Video')
        sanitized_title = sanitize_filename(raw_title)

        expected_file = os.path.join(temp_dir, f"{video_id}.mp3")
        if not os.path.exists(expected_file):
            raise FileNotFoundError("Audio download failed or file missing.")

        return expected_file, sanitized_title, info

import re
from youtube_transcript_api import YouTubeTranscriptApi
from utils import timecode_to_ms

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from standard, short, embed, or music URLs, or raw 11-char ID."""
    url = url.strip()
    if len(url) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", url):
        return url
    match = re.search(r"(?:v=|\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})", url)
    if not match:
        raise ValueError("Invalid YouTube URL or Video ID format.")
    return match.group(1)

def get_cuts_from_transcript(video_id: str) -> list[dict]:
    """Retrieves transcript and maps start positions to milliseconds."""
    try:
        # Support both youtube-transcript-api object and class API versions
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except AttributeError:
            transcript = YouTubeTranscriptApi().fetch(video_id)
            
        cuts = []
        for i, entry in enumerate(transcript):
            start = entry['start'] if isinstance(entry, dict) else getattr(entry, 'start', 0)
            text = entry['text'] if isinstance(entry, dict) else getattr(entry, 'text', '')
            start_ms = int(start * 1000)
            clean_text = text.replace('\n', ' ').strip()
            title = f"Track_{i+1:02d}_{clean_text[:25]}"
            cuts.append({"start_ms": start_ms, "title": title})
        return cuts
    except Exception as e:
        print(f"Notice: Transcript not available ({e}).")
        return []

def get_cuts_from_description(description: str) -> list[dict]:
    """
    Extracts timestamps and track titles from video description text.
    Matches lines containing timecodes like '00:00 Intro' or '01:23:45 Song Title'.
    """
    cuts = []
    if not description:
        return cuts
    
    pattern = re.compile(r'^\s*\(?\b(\d{1,2}:\d{2}(?::\d{2})?)\b\)?\s*[-–—]?\s*(.+)$', re.MULTILINE)
    for match in pattern.finditer(description):
        tc, title = match.group(1), match.group(2).strip()
        try:
            start_ms = timecode_to_ms(tc)
            cuts.append({"start_ms": start_ms, "title": title})
        except ValueError:
            continue
    return cuts

def get_cuts_from_video_info(info: dict) -> list[dict]:
    """
    Tries yt-dlp native chapters first, then fallbacks to description timestamps.
    """
    cuts = []
    chapters = info.get('chapters')
    if chapters:
        for i, ch in enumerate(chapters):
            start_ms = int(ch.get('start_time', 0) * 1000)
            title = ch.get('title', f'Track_{i+1:02d}')
            cuts.append({"start_ms": start_ms, "title": title})
        if cuts:
            return cuts

    desc = info.get('description', '')
    return get_cuts_from_description(desc)

def parse_manual_tracklist(file_path: str) -> list[dict]:
    """
    Parses a tracklist text file.
    Supports formats:
      - '00:13 Perfect by Ed Sheeran'
      - 'Perfect by Ed Sheeran (0:13 - 3:19)'
      - '01:01:13 Set Fire to the Rain by Adele'
    """
    cuts = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.search(r'\b(\d{1,2}:\d{2}(?::\d{2})?)\b', line)
            if match:
                tc = match.group(1)
                clean_title = re.sub(r'\(?\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:[-–—]\s*\d{1,2}:\d{2}(?::\d{2})?)?\s*\)?', '', line)
                clean_title = clean_title.strip(' -–—:()[]')
                if not clean_title:
                    clean_title = f"Track_{len(cuts)+1:02d}"
                try:
                    start_ms = timecode_to_ms(tc)
                    cuts.append({"start_ms": start_ms, "title": clean_title})
                except ValueError:
                    continue
    return cuts
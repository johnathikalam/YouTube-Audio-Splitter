import os
from pydub import AudioSegment
from utils import sanitize_filename

def split_and_export(audio_file: str, cuts: list[dict], output_folder: str):
    """Slices audio file into track segments and saves them to output_folder."""
    print("Loading audio file into memory...")
    audio = AudioSegment.from_file(audio_file)
    total_len = len(audio)

    os.makedirs(output_folder, exist_ok=True)

    # Ensure cuts are sorted chronologically
    cuts = sorted(cuts, key=lambda x: x['start_ms'])

    for idx, cut in enumerate(cuts):
        start = cut['start_ms']
        if start >= total_len:
            break

        # Next cut point or end of file
        end = cuts[idx + 1]['start_ms'] if idx + 1 < len(cuts) else total_len
        if end <= start or (end - start) < 500:
            continue

        # Extract segment
        segment = audio[start:end]

        clean_title = sanitize_filename(cut['title'])
        filename = f"{idx+1:02d}_{clean_title}.mp3"
        out_path = os.path.join(output_folder, filename)

        print(f"Exporting [{idx+1}/{len(cuts)}]: {filename} ({len(segment)/1000:.1f}s)")
        segment.export(out_path, format="mp3", bitrate="192k")
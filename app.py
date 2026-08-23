import argparse
import os
import shutil
from utils import check_ffmpeg
from downloader import download_audio
from transcript_parser import (
    extract_video_id,
    get_cuts_from_transcript,
    get_cuts_from_video_info,
    parse_manual_tracklist
)

def main():
    parser = argparse.ArgumentParser(description="YouTube Transcript-Based Audio Splitter")
    parser.add_argument("--url", required=True, help="YouTube video URL")
    parser.add_argument("--tracks", help="Optional path to manual tracklist file")
    parser.add_argument("--out", default="output", help="Root output directory")
    args = parser.parse_args()

    # Step 0: Pre-flight checks
    check_ffmpeg()
    from splitter import split_and_export

    try:
        video_id = extract_video_id(args.url)
    except ValueError as ve:
        print(f"Error: {ve}")
        return

    cuts = []

    # Step 1: Check manual tracklist if provided
    if args.tracks:
        print(f"Reading manual tracklist from: {args.tracks}")
        cuts = parse_manual_tracklist(args.tracks)

    # Step 2: Try fetching video transcript
    if not cuts:
        print("Fetching video transcript...")
        cuts = get_cuts_from_transcript(video_id)

    # Step 3: Download media audio & extract metadata
    temp_dir = "temp"
    try:
        print("Downloading YouTube audio...")
        audio_file, video_title, video_info = download_audio(args.url, temp_dir=temp_dir)

        # Step 4: If no transcript, try video chapters / description fallback
        if not cuts:
            print("Transcript unavailable. Attempting to parse video description chapters/timestamps...")
            cuts = get_cuts_from_video_info(video_info)

        if not cuts:
            print("\nError: No valid split points found via transcript, chapters, or manual tracklist. Aborting.")
            return

        print(f"Found {len(cuts)} split point(s). Starting audio segmentation...")

        # Step 5: Split and save output
        target_folder = os.path.join(args.out, video_title)
        split_and_export(audio_file, cuts, target_folder)

        print(f"\nSuccess! Tracks exported to: {target_folder}")

    except Exception as e:
        print(f"Processing failed: {e}")

    finally:
        # Cleanup temporary audio files
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
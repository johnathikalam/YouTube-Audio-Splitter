# 🎵 YouTube Audio Splitter

A full-stack Python & React application that downloads audio from YouTube videos, mixes, podcasts, or music albums, parses timestamps from transcripts, description chapters, or custom tracklists, and splits the audio into separate downloadable MP3 tracks.

---

## ✨ Features

- **🎨 Modern Responsive React UI**: Sleek dark-mode interface built with React & Vite, optimized for desktop, tablet, and mobile screens.
- **📄 Flexible Tracklist Parsing**: Supports multiple timestamp formats:
  - Range format: `Girls Like You by Maroon 5 (0:07 - 3:55)`
  - Standard format: `00:00 Intro` or `01:23:45 Song Title`
  - Automatic fallback to official YouTube subtitles/transcripts or description chapters if no tracklist is provided.
- **⚡ Ephemeral & Zero Server Persistence**: All downloads and track slicing occur in temporary, session-isolated folders that are automatically purged after files are downloaded.
- **📦 Dual Export Options**: Download the full output folder as a `.zip` archive or download individual MP3 tracks on demand.
- **💻 CLI & Full-Stack Web App**: Run via web browser UI or command line (CLI).

---

## 📁 Project Structure

```text
youtube_song_splitter/
├── app.py                # Command Line Interface (CLI) runner
├── server.py             # FastAPI backend API server
├── downloader.py         # Audio extraction module using yt-dlp
├── transcript_parser.py  # Subtitle, chapter, and tracklist parser
├── splitter.py           # Audio slicing engine powered by pydub & FFmpeg
├── utils.py              # System PATH check & helper utilities
├── run_local.py          # One-click full-stack local server launcher
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container definition for server deployment
├── DEPLOYMENT.md        # Guide for Cloudflare Pages & Render deployment
├── README.md            # Project documentation
└── frontend/             # React UI application (Vite)
    ├── src/
    │   ├── App.jsx       # Main React component
    │   └── App.css       # Mobile-responsive CSS styles
    └── package.json
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **FFmpeg** (On Windows, FFmpeg is automatically detected via system PATH or `static-ffmpeg`)

### 1. Clone & Install Dependencies

```powershell
# Install Python dependencies
pip install -r requirements.txt

# Install React frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Launch the Application

Run the unified full-stack launcher:

```powershell
python run_local.py
```

- **React Web UI**: Open **[http://localhost:5173](http://localhost:5173)** in your browser.
- **FastAPI API Docs**: Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.

---

## 🖥️ Command Line Usage (CLI Mode)

You can also process YouTube videos directly from your terminal:

```powershell
# Automatic transcript / chapter splitting
python app.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Split using a custom tracklist file
python app.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --tracks tracklist.txt
```

### Sample `tracklist.txt` format:
```text
Girls Like You by Maroon 5 (0:07 - 3:55)
Let Her Go by Passenger (4:02 - 7:28)
Shape of You by Ed Sheeran (7:30 - 11:15)
```

---

## 🌐 Cloudflare & Container Deployment

To deploy this application to production:
1. **React UI**: Deploy `frontend/` on **Cloudflare Pages** (Free CDN).
2. **Backend API**: Deploy `server.py` on **Render** or **Railway** using the included [`Dockerfile`](file:///c:/Users/johna/Documents/projects/python/youtube_song_splitter/Dockerfile).

For detailed step-by-step instructions, see [`DEPLOYMENT.md`](file:///c:/Users/johna/Documents/projects/python/youtube_song_splitter/DEPLOYMENT.md).

---

## 📄 License

MIT License. Open source for testing and personal use.

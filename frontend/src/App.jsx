import React, { useState } from 'react';
import { Music, Video, Download, Scissors, CheckCircle, AlertCircle, Loader2, FolderArchive, FileAudio } from 'lucide-react';
import './App.css';

const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();
const API_BASE = configuredApiUrl ? configuredApiUrl.replace(/\/$/, '') : '';

const DEFAULT_TRACKLIST = `Girls Like You by Maroon 5 (0:07 - 3:55)
Let Her Go by Passenger (4:02 - 7:28)`;

export default function App() {
  const [url, setUrl] = useState('');
  const [tracklist, setTracklist] = useState(DEFAULT_TRACKLIST);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSplit = async (e) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please provide a valid YouTube video URL.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setStatusMessage('Downloading audio and parsing tracks from YouTube...');

    try {
      if (!API_BASE) {
        throw new Error('The backend URL is not configured. Set VITE_API_URL in Cloudflare Pages and redeploy the frontend.');
      }

      const response = await fetch(`${API_BASE}/api/split`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          "bypass-tunnel-reminder": "true",
        },
        body: JSON.stringify({
          url: url.trim(),
          tracklist: tracklist.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to split audio.');
      }

      setResult(data);
      setStatusMessage('');
    } catch (err) {
      console.error(`Fetch error targeting API [${API_BASE}]:`, err);
      if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        setError(`Failed to connect to backend server at [${API_BASE}]. Please verify your VITE_API_URL environment variable in Cloudflare settings or check if your Render backend is awake.`);
      } else {
        setError(err.message || 'An unexpected error occurred while processing.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadZip = () => {
    if (result && result.download_zip) {
      window.location.href = `${API_BASE}${result.download_zip}`;
    }
  };

  const handleDownloadTrack = (track) => {
    if (track && track.download_url) {
      window.location.href = `${API_BASE}${track.download_url}`;
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo-badge">
          <Music size={28} className="icon-pulse" />
        </div>
        <h1>YouTube Audio Splitter</h1>
        <p className="subtitle">
          Download long music mixes, compilations, or albums and split them into separate MP3 track files.
        </p>
      </header>

      <main className="main-content">
        <form onSubmit={handleSplit} className="card form-card">
          <div className="input-group">
            <label htmlFor="url-input">
              <Video className="input-icon youtube-color" size={20} />
              YouTube Video URL
            </label>
            <input
              id="url-input"
              type="text"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
              required
              autoComplete="off"
              spellCheck={false}
              data-gramm="false"
              data-enable-grammarly="false"
            />
          </div>

          <div className="input-group">
            <label htmlFor="tracklist-input">
              <Scissors className="input-icon" size={20} />
              Track List (Timestamps & Song Names)
            </label>
            <textarea
              id="tracklist-input"
              rows={6}
              placeholder={`Girls Like You by Maroon 5 (0:07 - 3:55)\nLet Her Go by Passenger (4:02 - 7:28)`}
              value={tracklist}
              onChange={(e) => setTracklist(e.target.value)}
              disabled={loading}
              spellCheck={false}
              data-gramm="false"
              data-enable-grammarly="false"
            />
            <span className="input-help">
              Format: <code>Song Title (0:07 - 3:55)</code> or <code>00:00 Song Title</code>. Leave empty to auto-detect transcript/chapters.
            </span>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="spinner" size={20} />
                Processing Audio...
              </>
            ) : (
              <>
                <Scissors size={20} />
                Split & Export Tracks
              </>
            )}
          </button>
        </form>

        {loading && (
          <div className="card status-card">
            <Loader2 className="spinner large" size={32} />
            <p>{statusMessage}</p>
            <span className="sub-status">This may take 15-45 seconds depending on video length.</span>
          </div>
        )}

        {error && (
          <div className="card error-card">
            <AlertCircle size={24} />
            <div>
              <h4>Processing Failed</h4>
              <p>{error}</p>
            </div>
          </div>
        )}

        {result && (
          <div className="card result-card">
            <div className="result-header">
              <div className="result-title-section">
                <CheckCircle className="success-icon" size={28} />
                <div>
                  <h3>{result.video_title}</h3>
                  <span className="badge">{result.total_tracks} Tracks Exported</span>
                </div>
              </div>

              <button onClick={handleDownloadZip} className="download-zip-btn">
                <FolderArchive size={20} />
                Download Output Folder (.zip)
              </button>
            </div>

            <div className="track-list-section">
              <h4>Exported Track Files</h4>
              <div className="track-grid">
                {result.tracks.map((track) => (
                  <div key={track.index} className="track-item">
                    <div className="track-info">
                      <FileAudio size={18} className="audio-icon" />
                      <span className="track-name">{track.filename}</span>
                      <span className="track-size">{track.size_mb} MB</span>
                    </div>
                    <button
                      onClick={() => handleDownloadTrack(track)}
                      className="track-download-btn"
                      title="Download individual track MP3"
                    >
                      <Download size={15} />
                      Download
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

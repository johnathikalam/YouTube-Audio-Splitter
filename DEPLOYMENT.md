# Deployment Guide: Cloudflare Pages + Container Backend

This guide outlines how to deploy your **YouTube Audio Splitter** application.

---

## 1. Cloudflare Architecture Overview

Cloudflare Pages & Workers run JavaScript at the edge and **cannot execute native Python code or FFmpeg binaries directly**.

The recommended architecture is:
- **Frontend (React UI)**: Deployed on **Cloudflare Pages** (Free, fast global CDN).
- **Backend (Python + FFmpeg API)**: Deployed on a container service like **Render**, **Railway**, or **Fly.io** using the included [`Dockerfile`](file:///c:/Users/johna/Documents/projects/python/youtube_song_splitter/Dockerfile).

---

## Step 1: Deploy Backend API (Render / Railway / Docker)

### Option A: Render (Free Tier)
1. Push your codebase to a GitHub/GitLab repository.
2. Log into [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Choose **Docker** as the Environment (Render will automatically detect the [`Dockerfile`](file:///c:/Users/johna/Documents/projects/python/youtube_song_splitter/Dockerfile)).
6. Click **Create Web Service**.
7. Once deployed, copy your backend URL (e.g. `https://yt-audio-splitter-api.onrender.com`).

---

## Step 2: Deploy React UI to Cloudflare Pages

1. Log into [Cloudflare Dashboard](https://dash.cloudflare.com).
2. Navigate to **Workers & Pages** -> **Create Application** -> **Pages** tab.
3. Select **Connect to Git** and choose your repository.
4. Configure Build Settings:
   - **Framework Preset**: `Vite`
   - **Root directory**: `frontend`
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
5. Environment Variables:
   - Add variable name: `VITE_API_URL`
   - Value: `https://yt-audio-splitter-api.onrender.com` (Your backend URL from Step 1)
6. Click **Save and Deploy**.

Your app is now live on Cloudflare Pages (e.g. `https://yt-audio-splitter.pages.dev`)!

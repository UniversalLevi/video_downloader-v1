# v1: Backend CLI Bridge Service (Railway Ready)

This service exposes a FastAPI endpoint to accept download requests from v2 (the web frontend/API). It uses yt-dlp and ffmpeg to download and merge videos, and streams the result back to v2.

## Features
- Accepts POST requests at /bridge-download with JSON: { "url": "...", "cookies": "..." (optional) }
- Returns the video file as a streaming response.
- Secured with a shared secret (set via environment variable).
- Cleans up temp files after sending.

## Deployment (Railway)

1. **Set Environment Variables:**
   - `BRIDGE_SECRET`: Shared secret for secure communication with v2 (choose a strong value).

2. **Dependencies:**
   - Python 3.7+
   - All dependencies in `requirements.txt` (FastAPI, uvicorn, yt-dlp)
   - ffmpeg (Railway supports apt installs; see below)

3. **Install ffmpeg on Railway:**
   - Add a `railway.json` or use the Railway dashboard to add a post-build script:
     ```json
     {
       "build": {
         "commands": [
           "apt-get update && apt-get install -y ffmpeg"
         ]
       }
     }
     ```
   - Or, add a `postbuild.sh` with:
     ```sh
     #!/bin/sh
     apt-get update && apt-get install -y ffmpeg
     ```

4. **Start Command:**
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **Expose Port 8000** in Railway settings.

---

## Example Request

```json
POST /bridge-download
{
  "url": "https://...",
  "cookies": "..." // optional
}
Headers: x-bridge-secret: <your secret>
```

---

## Security
- Only v2 (with the correct secret) can access this service.
- Do not expose this endpoint to the public without the secret. 
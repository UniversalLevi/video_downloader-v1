from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import subprocess
import tempfile
import os
import uuid
import shutil
import yt_dlp

SHARED_SECRET = os.environ.get("BRIDGE_SECRET", "supersecret")

app = FastAPI()

def get_temp_dir():
    return tempfile.mkdtemp(prefix="dl_")

class DownloadRequest(BaseModel):
    url: str
    cookies: str = None

@app.post("/bridge-download")
async def bridge_download(req: Request, x_bridge_secret: str = Header(None)):
    if x_bridge_secret != SHARED_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid secret.")
    data = await req.json()
    url = data.get("url")
    cookies = data.get("cookies")
    if not url:
        return JSONResponse({"error": "Missing URL"}, status_code=400)
    temp_dir = get_temp_dir()
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }
        if cookies:
            cookies_path = os.path.join(temp_dir, 'cookies.txt')
            with open(cookies_path, 'w', encoding='utf-8') as f:
                f.write(cookies)
            ydl_opts['cookiefile'] = cookies_path
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        if not os.path.exists(filename):
            raise Exception("Download failed.")
        return FileResponse(filename, filename=os.path.basename(filename), media_type='application/octet-stream')
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        # Clean up temp dir after response is sent
        shutil.rmtree(temp_dir, ignore_errors=True) 
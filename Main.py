#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python3
"""FastAPI backend for face‑shape detection + YouTube recommender (no gender input)."""

from pathlib import Path
import os, shutil, cv2, uvicorn
from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# ---------------------------------------------------------------------------
# local imports – adjust the paths to match your project layout
# ---------------------------------------------------------------------------
import sys
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))  # so we can `import Faceshape_Pipeline`

import Faceshape_Pipeline as fp
import Recommend_videos   as rv

app = FastAPI()

# ---------------------------------------------------------------------------
# Jinja2 template directory
# ---------------------------------------------------------------------------
TEMPLATE_DIR = PROJECT_ROOT / "templates"
TEMPLATE_DIR.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# ---------------------------------------------------------------------------
# Absolute path to the SQLite database with video metadata
# ---------------------------------------------------------------------------
DB_PATH = (PROJECT_ROOT / "data" / "youtube.db").resolve()
DB_PATH.parent.mkdir(exist_ok=True)  # ensure /data folder exists

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the upload form."""
    return templates.TemplateResponse("index_v5.html", {"request": request})


@app.post("/api/analyze")
async def analyze(
    ethnicity: str        = Form(...),
    file:      UploadFile = File(...)
):
    """Receive an image & ethnicity, predict face‑shape, return video list."""

    # --- Save upload temporarily --------------------------------------------
    temp_path = PROJECT_ROOT / f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # --- Predict face shape --------------------------------------------------
    image       = cv2.imread(str(temp_path))
    predictor   = fp.FaceShapePredictor()
    result      = predictor.predict(image)  # expect {"face_shape": "Oval", ...}
    face_shape  = result.get("face_shape", "Unknown")

    # --- Clean up ------------------------------------------------------------
    temp_path.unlink(missing_ok=True)

    # --- Fetch video recommendations ----------------------------------------
    recs = rv.recommend_videos(face_shape, ethnicity, database_name=str(DB_PATH))

    return JSONResponse({
        "face_shape":      face_shape,
        "ethnicity":       ethnicity,
        "recommendations": recs,
    })


if __name__ == "__main__":
    uvicorn.run("Main:app", host="0.0.0.0", port=8000, reload=True)


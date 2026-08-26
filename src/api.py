"""
Argus-AI API
------------
FastAPI wrapper around the Detection -> Verification -> Response -> Report
pipeline (main.py), so the React frontend can call it over HTTP.

Run:
    uvicorn src.api:app --reload --port 8000

Endpoints:
    POST /analyze         - upload an image + city, run the full pipeline,
                             return the JSON report (+ a URL to the PDF)
    GET  /reports/{name}  - download a generated PDF report
    GET  /health          - simple health check
"""

import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from main import run_pipeline, DEFAULT_REPORTS_DIR

# Resolve everything relative to the project root (one level above src/),
# regardless of the working directory uvicorn was launched from. Also
# chdir into it, since response_agent.py's knowledge_base lookup ("data/
# knowledge_base") and other relative paths deeper in the pipeline assume
# project-root as cwd (this matches how `python src/main.py` behaves).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")
REPORTS_DIR = os.path.join(PROJECT_ROOT, DEFAULT_REPORTS_DIR)
FIRE_MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "fire_detection", "best.pt")
LANDSLIDE_MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "landslide_classification", "best_model.pt")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

app = FastAPI(title="Argus-AI API", version="1.0")

# Allow the local React dev server to call this API. Tighten this to your
# deployed frontend's exact origin before shipping to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    city: str = Form(...),
    mode: str = Form("both"),
):
    """
    Accepts an uploaded image + city name, runs the full Argus-AI pipeline,
    and returns the combined report as JSON. The PDF report path in the
    response can be fetched via GET /reports/{filename}.
    """
    if mode not in ("fire", "landslide", "both"):
        raise HTTPException(status_code=400, detail="mode must be 'fire', 'landslide', or 'both'")

    ext = os.path.splitext(image.filename or "")[1] or ".jpg"
    saved_name = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_name)

    with open(saved_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    try:
        report = run_pipeline(
            image_path=saved_path,
            city=city,
            fire_model_path=FIRE_MODEL_PATH,
            landslide_model_path=LANDSLIDE_MODEL_PATH,
            mode=mode,
            reports_dir=REPORTS_DIR,
            generate_pdf=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if "pdf_path" in report:
        report["pdf_url"] = f"/reports/{os.path.basename(report['pdf_path'])}"

    return report


@app.get("/reports/{filename}")
def get_report(filename: str):
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, media_type="application/pdf", filename=filename)
# app/main.py
import os, time, uuid, logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import numpy as np
import onnxruntime as ort
from typing import Tuple
import io
from google.cloud import storage

# ---- logging: simple stdout text logs ----
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
log = logging.getLogger("reid")

# ---- model/env ----
INPUT_H = int(os.getenv("INPUT_H", 224))
INPUT_W = int(os.getenv("INPUT_W", 224))
MODEL_PATH = os.getenv("MODEL_PATH", "/models/reid_swinb_1024.onnx")
# New: GPU toggle (default false). Accepts values like "true/1/yes" (case-insensitive)
GPU_ENV = os.getenv("GPU", "false")
GPU_ENABLED = str(GPU_ENV).strip().lower() in {"1", "true", "yes", "on"}

# Prefer explicit provider selection when GPU is enabled
providers = None
provider_options = None
if GPU_ENABLED:
    # Try CUDA first; if not available, fall back to CPU
    try:
        available = ort.get_available_providers()
        if "CUDAExecutionProvider" in available:
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            provider_options = [{}, {}]
            log.info("GPU requested and CUDAExecutionProvider is available. Using CUDA -> CPU fallback.")
        else:
            log.warning("GPU requested but CUDAExecutionProvider not available. Falling back to CPU.")
    except Exception as e:
        log.exception("Error checking available providers; falling back to default provider selection.")

# Create inference session (with providers if set)
try:
    if providers is not None:
        session = ort.InferenceSession(MODEL_PATH, providers=providers, provider_options=provider_options)
    else:
        session = ort.InferenceSession(MODEL_PATH)
except Exception as e:
    log.exception("Failed to create ONNX Runtime InferenceSession")
    raise

in_name = session.get_inputs()[0].name
out_name = session.get_outputs()[0].name
log.info(f"model loaded path={MODEL_PATH} input={INPUT_H}x{INPUT_W} providers={session.get_providers()} gpu_enabled={GPU_ENABLED}")

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/embed")
async def embed(file: UploadFile = File(...)):
    rid = uuid.uuid4().hex[:8]  # short request id
    t0 = time.perf_counter()
    try:
        img = Image.open(file.file).convert("RGB")
        orig = (img.width, img.height)
        img = img.resize((INPUT_W, INPUT_H))
        arr = (np.asarray(img).astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
        t1 = time.perf_counter()
        out = session.run([out_name], {in_name: arr})[0]  # shape: (1, D)
        emb = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-12)
        t2 = time.perf_counter()

        pre_ms = (t1 - t0) * 1000
        infer_ms = (t2 - t1) * 1000
        log.info(
            "embed ok rid=%s orig=%sx%s resized=%sx%s pre=%.1fms infer=%.1fms vec_shape=%s",
            rid, orig[0], orig[1], INPUT_W, INPUT_H, pre_ms, infer_ms, emb.shape
        )
        # return the vector — do NOT log vector contents
        return {"id": rid, "embedding": emb[0].tolist()}
    except Exception as e:
        log.exception("embed fail rid=%s", rid)
        raise HTTPException(status_code=400, detail=str(e))

# NEW: helper to parse and download gs:// URIs
def _parse_gs_uri(uri: str) -> Tuple[str, str]:
    if not uri.startswith("gs://") or len(uri) <= 5:
        raise ValueError("Invalid GCS URI")
    path = uri[5:]
    parts = path.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("GCS URI must be in the form gs://bucket/object")
    return parts[0], parts[1]

def _download_gcs_bytes(gs_uri: str) -> bytes:
    if storage is None:
        raise RuntimeError("google-cloud-storage is not installed")
    bucket_name, blob_name = _parse_gs_uri(gs_uri)
    client = storage.Client()  # uses default credentials
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if not blob.exists():
        raise FileNotFoundError(f"GCS object not found: {gs_uri}")
    return blob.download_as_bytes()

@app.post("/embed_gcs")
async def embed_gcs(payload: dict):
    rid = uuid.uuid4().hex[:8]
    t0 = time.perf_counter()
    try:
        gs_uri = payload.get("gs_uri")
        if not gs_uri:
            raise HTTPException(status_code=400, detail="Missing 'gs_uri'")
        # Download image bytes from GCS
        data = _download_gcs_bytes(gs_uri)
        img = Image.open(io.BytesIO(data)).convert("RGB")
        orig = (img.width, img.height)
        img = img.resize((INPUT_W, INPUT_H))
        arr = (np.asarray(img).astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
        t1 = time.perf_counter()
        out = session.run([out_name], {in_name: arr})[0]
        emb = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-12)
        t2 = time.perf_counter()

        pre_ms = (t1 - t0) * 1000
        infer_ms = (t2 - t1) * 1000
        log.info(
            "embed_gcs ok rid=%s uri=%s orig=%sx%s resized=%sx%s pre=%.1fms infer=%.1fms vec_shape=%s",
            rid, gs_uri, orig[0], orig[1], INPUT_W, INPUT_H, pre_ms, infer_ms, emb.shape
        )
        return {"id": rid, "embedding": emb[0].tolist()}
    except HTTPException:
        raise
    except Exception as e:
        log.exception("embed_gcs fail rid=%s", rid)
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
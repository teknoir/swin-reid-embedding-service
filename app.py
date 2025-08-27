# app/main.py
import os, time, uuid, logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import numpy as np
import onnxruntime as ort

# ---- logging: simple stdout text logs ----
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
log = logging.getLogger("reid")

# ---- model/env ----
INPUT_H = int(os.getenv("INPUT_H", 256))
INPUT_W = int(os.getenv("INPUT_W", 128))
MODEL_PATH = os.getenv("MODEL_PATH", "/models/reid_swinb_1024.onnx")

providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
session = ort.InferenceSession(MODEL_PATH, providers=providers)
in_name = session.get_inputs()[0].name
out_name = session.get_outputs()[0].name
log.info(f"model loaded path={MODEL_PATH} input={INPUT_H}x{INPUT_W} providers={session.get_providers()}")

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

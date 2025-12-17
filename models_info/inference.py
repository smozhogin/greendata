

import re
from io import BytesIO

import torch
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

MODEL_ID = "kazars24/trocr-base-handwritten-ru"


KEEP_ONLY = re.compile(r"[^а-яё0-9\-\s]+", flags=re.IGNORECASE)

def clean_text(s: str) -> str:
    s = "" if s is None else str(s)
    s = s.lower().replace("ё", "е")
    s = s.replace("\t", " ").replace("\r", " ").replace("\n", " ").replace("\f", " ")
    s = KEEP_ONLY.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s

app = FastAPI(title="TrOCR RU (no-finetune)")

device = "cuda" if torch.cuda.is_available() else "cpu"
processor = TrOCRProcessor.from_pretrained(MODEL_ID)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_ID).to(device)
model.eval()

model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.eos_token_id = processor.tokenizer.sep_token_id


@app.post("/ocr")
async def ocr_image(
    file: UploadFile = File(...),
    max_new_tokens: int = Query(32, ge=1, le=128),
    num_beams: int = Query(1, ge=1, le=8),
    normalize: bool = Query(True),
) -> dict:
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Please upload an image file.")

    data = await file.read()
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot read image: {e}")

    inputs = processor(images=img, return_tensors="pt").to(device)

    with torch.no_grad():
        if device == "cuda":
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                gen_ids = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    num_beams=num_beams,
                )
        else:
            gen_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                num_beams=num_beams,
            )

    pred = processor.batch_decode(gen_ids, skip_special_tokens=True)[0]
    pred = clean_text(pred) if normalize else pred

    return {"text": pred, "model_id": MODEL_ID, "device": device}

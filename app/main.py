
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io, sys

sys.path.append("/content")
from pipeline import analyze_food

app = FastAPI(title="Multimodal Recipe Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.get("/")
def root():
    return {"status": "running", "message": "Recipe Generator API is live"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze(
    image        : UploadFile = File(...),
    instructions : str        = Form(default="")
):
    image_bytes = await image.read()
    pil_image   = Image.open(io.BytesIO(image_bytes))
    result      = analyze_food(pil_image, instructions)
    return result

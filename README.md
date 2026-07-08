# 🍽️ Multimodal Recipe Generator

> Upload a food photo → Get a complete recipe + nutrition analysis instantly

---

## 📌 Overview

A full-stack multimodal AI application that:
1. **Identifies food** from an uploaded image using a fine-tuned BLIP model
2. **Generates recipes** — standard via Spoonacular API, or custom via Mistral 7B / Qwen 2.5-72B
3. **Provides nutrition** with precise per-serving macronutrient data

---

## 🏗️ Architecture

[Food Image] ──► BLIP (fine-tuned) ──► Food Label
│
┌────────────────────┤
│                    │
No instructions        Has instructions
│                    │
▼                    ▼
Spoonacular API       Mistral 7B / Qwen 72B
(recipe+nutrition)    (custom recipe)
│
▼
Spoonacular Nutrition API
│                   │
└───────────────────┘
│
▼
FastAPI Backend
│
▼
Streamlit Frontend

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Food Recognition | BLIP fine-tuned with LoRA on Food101 |
| LLM | Mistral 7B / Qwen 2.5-72B via HuggingFace |
| Recipe + Nutrition | Spoonacular API |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Fine-tuning | PEFT (LoRA) — only 0.635% of parameters trained |
| Containerization | Docker |
| Training | Google Colab T4 GPU |

---

## 📊 Model Performance

| Model | Method | Top-1 Accuracy |
|---|---|---|
| CLIP ViT-B/32 | Zero-shot baseline | 67.0% |
| BLIP base | Fine-tuned with LoRA | ~80%+ |

**+13% improvement** through LoRA fine-tuning on Food101

---

## 🚀 Getting Started

```bash
git clone https://github.com/YOUR_USERNAME/multimodal-recipe-generator.git
cd multimodal-recipe-generator
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
```

### Run locally
```bash
# Terminal 1
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2
streamlit run app/streamlit_app.py --server.port 8501
```

### Docker
```bash
docker build -t recipe-generator .
docker run -p 8000:8000 -p 8501:8501 \
  -e HF_TOKEN=your_token \
  -e SPOONACULAR_KEY=your_key \
  recipe-generator
```

---

## 📁 Project Structure

multimodal-recipe-generator/
├── app/
│   ├── pipeline.py        # ML pipeline (BLIP + Spoonacular + Mistral)
│   ├── main.py            # FastAPI server
│   └── streamlit_app.py   # Streamlit UI
├── notebooks/
│   ├── week1_clip_zeroshot.ipynb
│   ├── week2_recipe_pipeline.ipynb
│   └── week3_blip2_finetune.ipynb
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md

---

## 📝 Skills Demonstrated

- Multimodal Learning (Vision + Language)
- Transfer Learning + LoRA Fine-Tuning
- LLM Prompt Engineering
- REST API Design (FastAPI)
- Interactive ML Frontend (Streamlit)
- Docker Containerization
- API Integration (HuggingFace, Spoonacular)

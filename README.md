
# 🍽️ Multimodal Recipe Generator

A multimodal AI application that generates complete recipes from a food image with optional dietary text instructions.

The system combines **computer vision**, **large language models**, and **recipe retrieval** to generate accurate, customizable recipes along with nutritional information.

---

## Features

- 📷 Recognizes food from uploaded images using a fine-tuned BLIP model
- 🧠 Supports optional dietary text instructions for recipe customization
- 📚 Retrieves existing recipes from Spoonacular whenever available
- 🤖 Generates new recipes using Mistral AI when recipes are unavailable or customized
- 🥗 Enriches recipes with nutrition, cook time, servings, ingredients and preparation steps
- 🌐 Interactive Streamlit interface with FastAPI backend

---

# Pipeline

```
                Food Image
                     │
                     ▼
          Fine-tuned BLIP (Food101)
                     │
               Predicted Food
                     │
         ┌───────────┴────────────┐
         │                        │
 No dietary instructions   Dietary instructions
         │                        │
         ▼                        ▼
 Spoonacular API             Mistral AI
 (Recipe Retrieval)     (Recipe Generation)
         │                        │
         └───────────┬────────────┘
                     ▼
     Spoonacular Nutrition API
                     │
                     ▼
             FastAPI Backend
                     │
                     ▼
           Streamlit Frontend
```

---

# Model Training

The food recognition model was specialized for food classification using parameter-efficient fine-tuning.

- Base model: **BLIP**
- Dataset: **Food101**
- Fine-tuning: **LoRA (PEFT)**
- Training Platform: **Google Colab (T4 GPU)**

Performance

| Model | Accuracy |
|--------|---------:|
| CLIP (Zero-shot) | 67% |
| Fine-tuned BLIP | ~85% |

The fine-tuned BLIP model significantly improves recognition accuracy over the zero-shot CLIP baseline.

---

# Technology Stack

| Component | Technology |
|------------|------------|
| Vision Model | BLIP |
| Baseline | CLIP |
| Fine-tuning | LoRA (PEFT) |
| Dataset | Food101 |
| Recipe Retrieval | Spoonacular API |
| Recipe Generation | Mistral AI |
| Nutrition | Spoonacular API |
| Backend | FastAPI |
| Frontend | Streamlit |
| Deployment | Docker |
| Training | Google Colab |

---

# Project Structure

```
multimodal-recipe-generator/
│
├── app/
│   ├── pipeline.py
│   ├── main.py
│   ├── streamlit_app.py
│   └── utils.py
│
├── models/
│
├── notebooks/
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# Running the Project

Install dependencies

```bash
pip install -r requirements.txt
```

Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

Run the Streamlit frontend

```bash
streamlit run app/streamlit_app.py
```

---

# Skills Demonstrated

- Multimodal AI
- Vision-Language Models
- Transfer Learning
- Parameter-Efficient Fine-Tuning (LoRA)
- Prompt Engineering
- FastAPI
- Streamlit
- Docker
- API Integration
- Computer Vision
- Large Language Models

---

# Author

**Teja Sai Eswar**  
B.Tech, EECE Department 
IIT Kharagpur

📧 Email: tsereddy2022@gmail.com  
🔗 GitHub: https://github.com/CherrySeasons  

---

If you found this project interesting, feel free to ⭐ the repository or connect with me!


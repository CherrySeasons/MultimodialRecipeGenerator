
import torch
import requests
import json
import os
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from peft import PeftModel
from huggingface_hub import InferenceClient

BASE_MODEL = "Salesforce/blip-image-captioning-base"
LORA_PATH  = "/content/drive/MyDrive/Projects/Multimodial Recipe Generator/Models/blip_lora_best"
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[Pipeline] Loading on: {DEVICE}")

# Load processor
processor = BlipProcessor.from_pretrained(BASE_MODEL)
print("[Pipeline] Processor loaded ✓")

# Load base BLIP model
base_model = BlipForConditionalGeneration.from_pretrained(
    BASE_MODEL,
    torch_dtype = torch.float16 if DEVICE == "cuda" else torch.float32
)

# Try loading your fine-tuned LoRA weights
try:
    model = PeftModel.from_pretrained(base_model, LORA_PATH)
    print("[Pipeline] Fine-tuned BLIP (LoRA) loaded ✓")
except Exception as e:
    print(f"[Pipeline] LoRA weights not found: {e}")
    print("[Pipeline] Using base BLIP without fine-tuning")
    model = base_model

model = model.to(DEVICE)
model.eval()
print(f"[Pipeline] Model ready on {DEVICE} ✓")


def identify_food(image: Image.Image) -> dict:
    image = image.convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    pixel_values = inputs.pixel_values.to(DEVICE)
    if DEVICE == "cuda":
        pixel_values = pixel_values.half()
    with torch.no_grad():
        generated_ids = model.generate(
            pixel_values   = pixel_values,
            max_new_tokens = 10,
            num_beams      = 3
        )
    predicted = processor.decode(
        generated_ids[0],
        skip_special_tokens=True
    ).strip().lower()
    return {"food_label": predicted, "confidence": 85.0}


def get_recipe_spoonacular(food_label: str) -> dict:
    API_KEY = os.environ["SPOONACULAR_KEY"]
    search_resp = requests.get(
        "https://api.spoonacular.com/recipes/complexSearch",
        params={
            "query": food_label, "number": 1,
            "addRecipeNutrition": True, "apiKey": API_KEY
        }
    )
    if search_resp.status_code != 200:
        return None
    results = search_resp.json().get("results", [])
    if not results:
        return None
    recipe_id = results[0]["id"]
    detail_resp = requests.get(
        f"https://api.spoonacular.com/recipes/{recipe_id}/information",
        params={"includeNutrition": True, "apiKey": API_KEY}
    )
    if detail_resp.status_code != 200:
        return None
    data     = detail_resp.json()
    servings = data.get("servings", 4)
    ingredients = [i["original"] for i in data.get("extendedIngredients", [])]
    steps = []
    for instr in data.get("analyzedInstructions", []):
        for s in instr.get("steps", []):
            steps.append(f"Step {s['number']}: {s['step']}")
    nutrients_list = data.get("nutrition", {}).get("nutrients", [])
    nutrition = {}
    nmap = {
        "Calories": "calories", "Protein": "protein",
        "Carbohydrates": "carbs", "Fat": "fat", "Fiber": "fiber"
    }
    for n in nutrients_list:
        key = nmap.get(n["name"])
        if key:
            amt = round(n["amount"], 1)
            nutrition[key] = int(amt) if key == "calories" else f"{amt}{n['unit']}"
    return {
        "source": "spoonacular",
        "recipe_name": data.get("title", food_label),
        "cooking_time": data.get("readyInMinutes", "N/A"),
        "servings": servings,
        "ingredients": ingredients,
        "steps": steps,
        "nutrition": nutrition
    }


def get_nutrition_from_ingredients(ingredients: list, servings: int = 4) -> dict:
    API_KEY = os.environ["SPOONACULAR_KEY"]
    resp = requests.post(
        "https://api.spoonacular.com/recipes/parseIngredients",
        params={"apiKey": API_KEY},
        data={
            "ingredientList": "\n".join(ingredients),
            "servings": servings,
            "includeNutrition": True
        }
    )
    if resp.status_code != 200:
        return {}
    totals = {"calories":0,"protein":0,"carbs":0,"fat":0,"fiber":0}
    nmap   = {
        "Calories":"calories","Protein":"protein",
        "Carbohydrates":"carbs","Fat":"fat","Fiber":"fiber"
    }
    for ing in resp.json():
        for n in ing.get("nutrition",{}).get("nutrients",[]):
            key = nmap.get(n["name"])
            if key:
                totals[key] += n["amount"]
    return {
        "calories": round(totals["calories"]/servings),
        "protein" : f"{round(totals['protein']/servings,1)}g",
        "carbs"   : f"{round(totals['carbs']/servings,1)}g",
        "fat"     : f"{round(totals['fat']/servings,1)}g",
        "fiber"   : f"{round(totals['fiber']/servings,1)}g"
    }


def get_recipe_mistral(food_label: str, instructions: str) -> dict:
    client = InferenceClient(provider="novita", api_key=os.environ["HF_TOKEN"])
    prompt = f"""You are a professional chef.
Generate a recipe for: {food_label}
Special instructions: {instructions}
Respond ONLY in this exact JSON format:
{{
    "recipe_name": "name",
    "cooking_time": "X minutes",
    "servings": 4,
    "ingredients": ["qty + ingredient 1", "qty + ingredient 2"],
    "steps": ["Step 1: ...", "Step 2: ..."],
    "chef_note": "one tip"
}}"""
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct",
        messages=[{"role":"user","content":prompt}],
        max_tokens=800, temperature=0.7
    )
    generated = response.choices[0].message.content.strip()
    try:
        start  = generated.find("{")
        end    = generated.rfind("}") + 1
        recipe = json.loads(generated[start:end])
    except:
        return {"error": "Parse failed", "raw": generated}
    nutrition = get_nutrition_from_ingredients(
        recipe.get("ingredients",[]),
        recipe.get("servings",4)
    )
    return {
        "source"      : "mistral",
        "recipe_name" : recipe.get("recipe_name", food_label),
        "cooking_time": recipe.get("cooking_time","N/A"),
        "servings"    : recipe.get("servings",4),
        "ingredients" : recipe.get("ingredients",[]),
        "steps"       : recipe.get("steps",[]),
        "chef_note"   : recipe.get("chef_note",""),
        "nutrition"   : nutrition
    }


def analyze_food(image: Image.Image, user_instructions: str = "") -> dict:
    print(f"[Pipeline] Analyzing image...")
    identification = identify_food(image)
    food_label     = identification["food_label"]
    confidence     = identification["confidence"]
    print(f"[Pipeline] Identified: {food_label} ({confidence}%)")
    if user_instructions.strip() == "":
        print("[Pipeline] Path: Simple → Spoonacular")
        recipe = get_recipe_spoonacular(food_label)
        if not recipe:
            print("[Pipeline] Spoonacular failed → Mistral fallback")
            recipe = get_recipe_mistral(food_label, "")
    else:
        print(f"[Pipeline] Path: Custom → Mistral")
        recipe = get_recipe_mistral(food_label, user_instructions)
    if recipe:
        recipe["food_label"]  = food_label
        recipe["confidence"]  = confidence
    return recipe

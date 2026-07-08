
import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(
    page_title="Multimodal Recipe Generator",
    page_icon="🍽️",
    layout="wide"
)

st.markdown("""
<style>
.big-title {
    font-size: 3.8rem !important;
    font-weight: 900 !important;
    color: #FF6B35 !important;
    text-align: center !important;
    line-height: 1.1 !important;
    margin-bottom: 0.2rem !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle {
    font-size: 1.15rem;
    color: #888;
    text-align: center;
    margin-bottom: 1.5rem;
}
.food-detected {
    font-size: 1.6rem;
    font-weight: 700;
    color: #2c3e50;
    text-align: center;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    border-radius: 12px;
    border-left: 5px solid #FF6B35;
    margin: 1rem 0;
}
.meta-card {
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.meta-value {
    font-size: 1.9rem;
    font-weight: 700;
    margin: 0;
    line-height: 1;
}
.meta-label {
    font-size: 0.8rem;
    color: #777;
    margin: 4px 0 0 0;
}
.nutr-card {
    border-radius: 10px;
    padding: 0.75rem;
    text-align: center;
    margin: 0.2rem;
}
.nutr-value {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
}
.nutr-label {
    font-size: 0.8rem;
    color: #666;
    margin: 2px 0 0 0;
}
.ingredient-item {
    padding: 6px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 0.95rem;
}
.step-item {
    padding: 10px 0;
    border-bottom: 1px solid #f0f0f0;
    line-height: 1.6;
}
.chef-note {
    background: #e8f5e9;
    border-radius: 8px;
    padding: 1rem;
    border-left: 4px solid #43a047;
    margin-top: 1rem;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

# Big Title
st.markdown(
    '<p class="big-title">🍽️ Multimodal Recipe Generator</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="subtitle">Upload a food photo • Get a complete recipe + nutrition instantly</p>',
    unsafe_allow_html=True
)
st.divider()

col_input, col_output = st.columns([1, 1.6], gap="large")

with col_input:
    st.subheader("📸 Your Input")
    uploaded_file = st.file_uploader(
        "Drop a food photo here",
        type=["jpg","jpeg","png","webp"]
    )
    if uploaded_file:
        st.image(
            Image.open(uploaded_file),
            caption="Your uploaded image",
            use_container_width=True
        )
    st.markdown("#### ✍️ Dietary Instructions")
    instructions = st.text_input(
        "Optional customization",
        placeholder="e.g. make it vegan • under 400 calories..."
    )
    if instructions.strip():
        st.info("🤖 Mistral AI generates a custom recipe")
    else:
        st.info("📚 Spoonacular database — fast + precise")
    btn = st.button(
        "✨ Generate Recipe",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None
    )

with col_output:
    st.subheader("📋 Recipe & Nutrition")
    if not uploaded_file:
        st.markdown("""
        <div style="text-align:center;color:#bbb;padding:4rem 2rem;">
            <div style="font-size:4rem;">🍕</div>
            <h3 style="color:#bbb;">Upload a food photo to begin</h3>
            <p>Your recipe and nutrition will appear here</p>
        </div>
        """, unsafe_allow_html=True)

    if btn and uploaded_file:
        with st.spinner("🔍 Identifying food and generating recipe..."):
            try:
                img_bytes = uploaded_file.getvalue()
                response  = requests.post(
                    "http://localhost:8000/analyze",
                    files   = {"image": ("food.jpg", img_bytes, "image/jpeg")},
                    data    = {"instructions": instructions},
                    timeout = 120
                )
                if response.status_code == 200:
                    result      = response.json()
                    api_success = True
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
                    api_success = False
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to FastAPI. Make sure it started correctly.")
                api_success = False
            except Exception as e:
                st.error(f"Error: {e}")
                api_success = False

        if api_success:
            food = result.get("food_label","Unknown").title()
            conf = result.get("confidence", 0)
            st.markdown(
                f'<div class="food-detected">🎯 Identified: {food} ({conf}% confidence)</div>',
                unsafe_allow_html=True
            )
            source = result.get("source","")
            if source == "spoonacular":
                st.success("📚 Source: Spoonacular Database")
            else:
                st.info("🤖 Source: Mistral AI (custom generated)")

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""
                <div class="meta-card" style="background:#fff3e0;">
                    <p class="meta-value" style="color:#FF6B35;">
                        {result.get("cooking_time","N/A")} min
                    </p>
                    <p class="meta-label">⏱️ Cook Time</p>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="meta-card" style="background:#e8f5e9;">
                    <p class="meta-value" style="color:#2e7d32;">
                        {result.get("servings","N/A")}
                    </p>
                    <p class="meta-label">👥 Servings</p>
                </div>""", unsafe_allow_html=True)
            with m3:
                cal = result.get("nutrition",{}).get("calories","N/A")
                st.markdown(f"""
                <div class="meta-card" style="background:#fce4ec;">
                    <p class="meta-value" style="color:#c62828;">
                        {cal}
                    </p>
                    <p class="meta-label">🔥 Cal/serving</p>
                </div>""", unsafe_allow_html=True)

            st.divider()
            tab_ing, tab_steps, tab_nutr = st.tabs([
                "🥗 Ingredients","👨‍🍳 Steps","📊 Nutrition"
            ])

            with tab_ing:
                st.markdown(f"### {result.get('recipe_name', food)}")
                for ing in result.get("ingredients",[]):
                    st.markdown(
                        f'<div class="ingredient-item">• {ing}</div>',
                        unsafe_allow_html=True
                    )

            with tab_steps:
                for step in result.get("steps",[]):
                    st.markdown(
                        f'<div class="step-item">{step}</div>',
                        unsafe_allow_html=True
                    )
                note = result.get("chef_note","")
                if note:
                    st.markdown(
                        f'<div class="chef-note">💡 Chef tip: {note}</div>',
                        unsafe_allow_html=True
                    )

            with tab_nutr:
                st.markdown("### Nutrition per serving")
                n    = result.get("nutrition",{})
                cols = st.columns(4)
                items = [
                    ("calories","🔥 Calories","#FF6B35","#fff3e0"),
                    ("protein", "💪 Protein", "#2e7d32","#e8f5e9"),
                    ("carbs",   "🌾 Carbs",   "#1565c0","#e3f2fd"),
                    ("fat",     "🧈 Fat",     "#6a1b9a","#f3e5f5"),
                ]
                for col,(key,label,color,bg) in zip(cols,items):
                    with col:
                        st.markdown(f"""
                        <div class="nutr-card" style="background:{bg};">
                            <p class="nutr-value" style="color:{color};">
                                {n.get(key,"N/A")}
                            </p>
                            <p class="nutr-label">{label}</p>
                        </div>""", unsafe_allow_html=True)
                fiber = n.get("fiber","N/A")
                st.markdown(f"""
                <div style="margin-top:0.5rem;padding:0.5rem 1rem;
                             background:#f5f5f5;border-radius:8px;
                             font-size:0.9rem;color:#555;">
                    🌿 Fiber: <strong>{fiber}</strong> per serving
                </div>""", unsafe_allow_html=True)

st.divider()
st.markdown("""
<p style="text-align:center;color:#bbb;font-size:0.8rem;">
    Multimodal Recipe Generator &nbsp;•&nbsp;
    BLIP + LoRA &nbsp;•&nbsp; Mistral 7B + Spoonacular &nbsp;•&nbsp;
    FastAPI + Streamlit
</p>
""", unsafe_allow_html=True)

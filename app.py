import streamlit as st
import json
import requests
from openai import OpenAI
import google.generativeai as genai
from streamlit_lottie import st_lottie

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="Etsy SEO Optimizer", page_icon="🛍️", layout="centered")

# --- MAGIC TRICK 1: Animated CSS Background + Text Contrast Fix ---
page_bg_css = """
<style>
/* 1. The Animated Background */
.stApp {
    background: linear-gradient(-45deg, #ff9a9e, #fecfef, #a1c4fd, #c2e9fb);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 2. The Glass Card */
[data-testid="stAppViewContainer"] > .main {
    background-color: rgba(255, 255, 255, 0.75); /* Slightly less transparent for better reading */
    border-radius: 15px;
    padding: 2rem;
    margin-top: 2rem;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}

/* 3. THE FIX: Force high-contrast dark text everywhere */
p, h1, h2, h3, h4, h5, h6, span, label {
    color: #1E293B !important; /* Dark slate gray */
}

/* 4. THE FIX: Make the output code blocks readable */
code {
    color: #0F172A !important; /* Very dark blue/black text */
    background-color: #FFFFFF !important; /* Solid white background */
    border-radius: 6px;
    padding: 10px;
    font-size: 16px !important;
    font-weight: 600;
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTION FOR LOTTIE ANIMATIONS
# ==========================================
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_anim = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_1cwng9r5.json")

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Settings")
    provider = st.selectbox("Choose AI Provider", ["Google Gemini (Free)", "OpenAI (Paid)"])
    api_key = st.text_input(f"Enter {provider.split(' ')[0]} API Key", type="password")
    
    if "Gemini" in provider:
        st.markdown("[Get your FREE Gemini key here](https://aistudio.google.com/app/apikey)")
    else:
        st.markdown("[Get your OpenAI key here](https://platform.openai.com/api-keys)")

# ==========================================
# 4. CORE AI FUNCTION (Fixed for Stable Gemini)
# ==========================================
def generate_etsy_seo(provider, api_key, product_desc):
    system_prompt = "You are an expert Etsy SEO copywriter. Output JSON with: 1. 'title' 2. 'tags' (list of 13) 3. 'description'."
    try:
        if "OpenAI" in provider:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={ "type": "json_object" },
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": product_desc}]
            )
            return json.loads(response.choices[0].message.content)
            
        elif "Gemini" in provider:
            # Using your installed google.generativeai library (v0.8.6)
            genai.configure(api_key=api_key)
            
            # THE FIX: Google's active 2026 free-tier model
            model = genai.GenerativeModel(
                model_name="gemini-3.5-flash",
                generation_config={"response_mime_type": "application/json"}
            )
            
            response = model.generate_content(system_prompt + "\n\nProduct:\n" + product_desc)
            return json.loads(response.text)
            
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 5. MAIN APP INTERFACE WITH ANIMATIONS
# ==========================================
col1, col2 = st.columns([1, 3])
with col1:
    if lottie_anim:
        st_lottie(lottie_anim, height=120, key="seo_animation")
with col2:
    st.title("🛍️ Etsy SEO Tag Generator")

st.write("Stop guessing. Generate proven, search-friendly titles and tags for your Etsy listings in seconds.")

product_description = st.text_area("What are you selling?", placeholder="e.g., A handmade wooden desk organizer...", height=100)

if st.button("Generate SEO Listing", type="primary"):
    if not api_key:
        st.error("⚠️ Please enter your API key in the sidebar first.")
    elif not product_description:
        st.warning("⚠️ Please describe your product.")
    else:
        with st.spinner(f"Analyzing trends using {provider.split(' ')[0]}..."):
            result = generate_etsy_seo(provider, api_key, product_description)
            
            if "error" in result:
                st.error(f"API Error: {result['error']}")
            else:
                st.balloons() 
                st.success("Listing Optimized!")
                st.subheader("📌 Optimized Title")
                st.code(result["title"], language=None)
                st.subheader("🏷️ 13 SEO Tags")
                st.code(", ".join(result["tags"]), language=None)
                st.subheader("📝 Product Description")
                st.write(result["description"])

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

/* ========================================
   1. ANIMATED GRADIENT BACKGROUND
======================================== */
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

/* ========================================
   2. GLASS CARD MAIN CONTAINER
======================================== */
[data-testid="stAppViewContainer"] > .main {
    background-color: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 2.2rem 2.5rem;
    margin-top: 1.5rem;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    border: 1px solid rgba(255, 255, 255, 0.4);
}

/* ========================================
   3. TEXT CONTRAST FIX
======================================== */
p, h1, h2, h3, h4, h5, h6, span, label, li, div[data-testid="stMarkdownContainer"] {
    color: #1E293B !important;
}
h1, h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

/* ========================================
   4. CODE BLOCKS
======================================== */
code {
    color: #0F172A !important;
    background-color: #FFFFFF !important;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 15px !important;
    font-weight: 600;
}
pre {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    padding: 14px !important;
    border: 1px solid rgba(0,0,0,0.08);
}

/* ========================================
   5. BUTTONS
======================================== */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #FFFFFF !important;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.4rem;
    font-weight: 600;
    box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(102, 126, 234, 0.55);
    color: #FFFFFF !important;
}
.stButton > button:active {
    transform: translateY(0px);
}

/* ========================================
   6. INPUTS, SELECTBOX, TEXTAREA
======================================== */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background-color: rgba(255, 255, 255, 0.9) !important;
    color: #1E293B !important;
    border-radius: 8px !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 8px !important;
    color: #1E293B !important;
}

/* ========================================
   7. SIDEBAR
======================================== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.65));
    backdrop-filter: blur(10px);
}
[data-testid="stSidebar"] * {
    color: #1E293B !important;
}

/* ========================================
   8. METRICS
======================================== */
[data-testid="stMetric"] {
    background-color: rgba(255, 255, 255, 0.85);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* ========================================
   9. TABS
======================================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background-color: rgba(255,255,255,0.6);
    border-radius: 8px 8px 0 0;
    color: #1E293B !important;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background-color: rgba(255,255,255,0.95) !important;
}

/* ========================================
   10. SCROLLBAR (optional polish)
======================================== */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(118, 75, 162, 0.5);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(118, 75, 162, 0.8);
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

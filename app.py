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
   0. FONTS
======================================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
}

/* ========================================
   1. BACKGROUND — subtle mesh, not a rainbow
======================================== */
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(124, 58, 237, 0.12) 0%, transparent 45%),
        radial-gradient(circle at 85% 10%, rgba(59, 130, 246, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 50% 90%, rgba(236, 72, 153, 0.08) 0%, transparent 45%),
        #0B0E14;
    background-attachment: fixed;
}

/* ========================================
   2. MAIN CONTAINER — clean card, real depth
======================================== */
[data-testid="stAppViewContainer"] > .main {
    background: rgba(17, 20, 28, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 3rem 3.5rem;
    margin: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.45),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

/* ========================================
   3. TYPOGRAPHY
======================================== */
p, span, label, li, div[data-testid="stMarkdownContainer"] {
    color: #CBD5E1 !important;
    font-size: 15.5px;
    line-height: 1.6;
}

h1, h2, h3, h4 {
    font-family: 'Sora', 'Inter', sans-serif !important;
    color: #F8FAFC !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em;
}

/* App title gets a gradient treatment automatically via first h1 */
h1 {
    background: linear-gradient(135deg, #F8FAFC 30%, #A78BFA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3.2rem !important;
    line-height: 1.1 !important;
    font-weight: 800 !important;
    letter-spacing: -0.01em;
    padding-bottom: 10px;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

/* Muted subheading text right under the title */
[data-testid="stMarkdownContainer"] > p:first-of-type {
    color: #94A3B8 !important;
    font-size: 1.2rem;
    font-weight: 400;
    max-width: 640px;
    margin-bottom: 1.8rem;
}

/* ========================================
   4. CODE BLOCKS
======================================== */
code {
    color: #C4B5FD !important;
    background-color: rgba(167, 139, 250, 0.12) !important;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 14px !important;
    font-weight: 600;
}
pre {
    background-color: #0D1017 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid rgba(255,255,255,0.08);
}

/* ========================================
   5. BUTTONS — premium gradient + glow
======================================== */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%);
    color: #FFFFFF !important;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: -0.01em;
    box-shadow:
        0 4px 14px rgba(124, 58, 237, 0.35),
        inset 0 1px 0 rgba(255,255,255,0.15);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow:
        0 8px 24px rgba(124, 58, 237, 0.5),
        inset 0 1px 0 rgba(255,255,255,0.2);
    color: #FFFFFF !important;
}
.stButton > button:active {
    transform: translateY(0px);
}
.stButton > button {
    width: auto !important;
    max-width: fit-content;
}


/* ========================================
   6. TEXT INPUTS / TEXTAREA
======================================== */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background-color: rgba(255, 255, 255, 0.04) !important;
    color: #F1F5F9 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    padding: 0.6rem 0.9rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #64748B !important;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.25) !important;
}
.stTextArea textarea {
    height: 100px !important;
    min-height: 100px !important;
}

/* ========================================
   7. SELECTBOX — fixed contrast (was invisible before)
======================================== */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
}
.stSelectbox div[data-baseweb="select"] span {
    color: #F1F5F9 !important;
}
/* Dropdown menu popover */
div[data-baseweb="popover"] li {
    background-color: #161A24 !important;
    color: #F1F5F9 !important;
}
div[data-baseweb="popover"] li:hover {
    background-color: rgba(124, 58, 237, 0.2) !important;
}

/* ========================================
   8. SIDEBAR — refined glass panel
======================================== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(17, 20, 28, 0.95), rgba(11, 14, 20, 0.98));
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}
[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    background: none !important;
    -webkit-text-fill-color: #F8FAFC !important;
    font-size: 1.15rem !important;
}
[data-testid="stSidebar"] label {
    color: #94A3B8 !important;
    font-size: 13px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="stSidebar"] a {
    color: #A78BFA !important;
    font-weight: 500;
}

/* ========================================
   9. METRICS
======================================== */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
}
[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-family: 'Sora', sans-serif !important;
}

/* ========================================
   10. TABS
======================================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border-radius: 8px 8px 0 0;
    color: #94A3B8 !important;
    font-weight: 600;
    padding: 10px 18px;
}
.stTabs [aria-selected="true"] {
    background-color: rgba(124, 58, 237, 0.12) !important;
    color: #C4B5FD !important;
    border-bottom: 2px solid #7C3AED;
}

/* ========================================
   11. EXPANDER / CONTAINER CARDS
======================================== */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}

/* ========================================
   12. DIVIDER
======================================== */
hr {
    border-color: rgba(255, 255, 255, 0.08) !important;
}

/* ========================================
   13. SCROLLBAR
======================================== */
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(124, 58, 237, 0.4);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(124, 58, 237, 0.7);
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
    provider = st.selectbox("Choose AI Provider", ["Google Gemini", "OpenAI"])
    api_key = st.text_input(f"Enter {provider.split(' ')[0]} API Key", type="password")
    
    if "Gemini" in provider:
        st.markdown("[Get your Gemini key here](https://aistudio.google.com/app/apikey)")
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

if st.button("Generate SEO Listing", type="primary",use_container_width=False):
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

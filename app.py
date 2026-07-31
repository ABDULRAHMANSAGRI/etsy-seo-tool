import streamlit as st
import json
from openai import OpenAI

# ==========================================
# 1. PAGE CONFIGURATION & SIDEBAR
# ==========================================
st.set_page_config(page_title="Etsy SEO Optimizer", page_icon="🛍️", layout="centered")

with st.sidebar:
    st.header("⚙️ Settings")
    # type="password" hides the key as they type it
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    st.markdown("[Get your API key here](https://platform.openai.com/api-keys)")
    st.markdown("---")
    st.caption("Your key is not stored. It is only used for this session.")

# ==========================================
# 2. CORE AI FUNCTION
# ==========================================
def generate_etsy_seo(api_key, product_desc):
    client = OpenAI(api_key=api_key)
    
    # The system prompt turns the AI into an Etsy expert
    system_prompt = """
    You are an expert Etsy SEO copywriter. Your goal is to help sellers rank on the first page of Etsy search.
    Given a rough product description, you must output a JSON object with exactly these three keys:
    1. "title": An SEO-optimized Etsy title (max 140 characters, using strong keywords separated by commas or pipes).
    2. "tags": A list of exactly 13 long-tail keyword tags (each tag must be 20 characters or less).
    3. "description": A highly engaging, 2-paragraph product description that highlights benefits and uses.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Fast, cheap, and smart enough for this task
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Product: {product_desc}"}
            ]
        )
        # Parse the JSON string returned by OpenAI into a Python dictionary
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 3. MAIN APP INTERFACE
# ==========================================
st.title("🛍️ Etsy SEO Tag & Title Generator")
st.write("Stop guessing. Generate proven, search-friendly titles and tags for your Etsy listings in seconds.")

# User Input
product_description = st.text_area(
    "What are you selling?",
    placeholder="e.g., A handmade wooden desk organizer with phone stand, made of walnut...",
    height=150
)

# Generate Button Logic
if st.button("Generate SEO Listing", type="primary"):
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar first.")
    elif not product_description:
        st.warning("⚠️ Please describe your product.")
    else:
        with st.spinner("Analyzing Etsy search trends & generating SEO..."):
            result = generate_etsy_seo(api_key, product_description)
            
            if "error" in result:
                st.error(f"API Error: {result['error']}")
            else:
                # Display Results beautifully
                st.success("Listing Optimized!")
                
                st.subheader("📌 Optimized Title")
                st.code(result["title"], language=None)
                
                st.subheader("🏷️ 13 SEO Tags")
                # Join tags into a comma-separated string for easy copy-pasting
                tags_str = ", ".join(result["tags"])
                st.code(tags_str, language=None)
                
                st.subheader("📝 Product Description")
                st.write(result["description"])
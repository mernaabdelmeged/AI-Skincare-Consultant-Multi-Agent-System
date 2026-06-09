import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import PIL.Image
import base64

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')


# ─────────────────────────────────────────────
# DATA LOADING FUNCTIONS
# ─────────────────────────────────────────────
@st.cache_data
def load_knowledge_base():
    try:
        with open("data/skincare_knowledge.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading knowledge base: {e}"

@st.cache_data
def load_products():
    try:
        return pd.read_csv("data/skincare_products.csv")
    except:
        return None

@st.cache_data
def load_csv_data(filepath):
    try:
        return pd.read_csv(filepath)
    except:
        return None

@st.cache_resource
def get_uploaded_book():
    book_path = "data/851832680-Skincare-E-book.pdf"
    id_file = "data/book_file_id.txt"

    if os.path.exists(id_file):
        try:
            with open(id_file, "r") as f:
                file_id = f.read().strip()
            file = genai.get_file(file_id)
            if file:
                return file
        except:
            pass

    try:
        file = genai.upload_file(path=book_path, display_name="Skincare_E_Book")
        import time
        while file.state.name == "PROCESSING":
            time.sleep(2)
            file = genai.get_file(file.name)
        with open(id_file, "w") as f:
            f.write(file.name)
        return file
    except Exception as e:
        st.error(f"Error uploading book: {e}")
        return None


# ─────────────────────────────────────────────
# AUTOMATED ACTION FUNCTIONS
# ─────────────────────────────────────────────
def save_prescription(patient_name, routine_text):
    os.makedirs("prescriptions", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = patient_name.replace(" ", "_") if patient_name else "patient"
    filename = f"prescriptions/{safe_name}_{timestamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Prescription for Patient: {patient_name}\n")
            f.write("="*40 + "\n\n")
            f.write(routine_text)
        return True, filename
    except Exception as e:
        return False, str(e)

def log_patient_data(patient_name, user_description, has_image):
    log_file = "data/patients_log.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(log_file):
        df = pd.DataFrame(columns=["Date", "Patient Name", "Complaint", "Uploaded Image"])
        df.to_csv(log_file, index=False, encoding="utf-8-sig")
    new_data = pd.DataFrame([{
        "Date": timestamp,
        "Patient Name": patient_name,
        "Complaint": user_description if user_description else "No text, Image only",
        "Uploaded Image": "Yes" if has_image else "No"
    }])
    new_data.to_csv(log_file, mode='a', header=False, index=False, encoding="utf-8-sig")


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Skincare Consultant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background: linear-gradient(135deg, #FFF0F5 0%, #FFF5FB 40%, #F0F4FF 100%);
    min-height: 100vh;
}

/* ── Hide Streamlit Chrome ── */
header { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 40px !important;
    max-width: 900px !important;
}
/* Force text in the main area to be dark (overriding Streamlit dark mode) */
.block-container .stMarkdown p, 
.block-container .stMarkdown li, 
.block-container .stMarkdown h1, 
.block-container .stMarkdown h2, 
.block-container .stMarkdown h3, 
.block-container .stMarkdown h4,
.block-container .stMarkdown strong,
.block-container .stMarkdown em,
.block-container .stMarkdown a,
.block-container .stMarkdown span,
.stMarkdown, .stMarkdown * {
    color: #1a1a2e !important;
}
/* Result card text */
.result-card, .result-card * {
    color: #1a1a2e !important;
}

/* ── Selection Color ── */
::selection {
    background: #FF6B9D;
    color: white;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%) !important;
    border-right: 1px solid rgba(255,105,180,0.2);
}
[data-testid="stSidebar"] * {
    color: #f0f0f0 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FF85A1 !important;
}
[data-testid="stSidebar"] .stMarkdown p {
    font-size: 12px !important;
    line-height: 1.6 !important;
    color: #c8c8d4 !important;
}
[data-testid="stSidebar"] .stMarkdown li {
    font-size: 12px !important;
    line-height: 1.8 !important;
    color: #c8c8d4 !important;
    white-space: nowrap !important;
}

/* ── Hero Section ── */
.hero-section {
    background: linear-gradient(135deg, #FF6B9D 0%, #C44BFF 50%, #FF6B9D 100%);
    background-size: 200% 200%;
    animation: gradientShift 6s ease infinite;
    border-radius: 18px;
    padding: 20px 30px;
    text-align: center;
    margin: 10px 0 20px 0;
    box-shadow: 0 15px 40px rgba(196,75,255,0.2);
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
    animation: rotate 10s linear infinite;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes rotate {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
.hero-title {
    font-size: 3rem;
    font-weight: 900;
    color: #ffffff;
    margin: 0 0 8px 0;
    letter-spacing: 2px;
    word-spacing: 2px;
    text-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.hero-subtitle {
    font-size: 1.15rem;
    color: rgba(255,255,255,0.95);
    font-weight: 500;
    margin: 0;
    letter-spacing: 0.3px;
}

/* ── Cards ── */
.card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 20px;
    border: 1px solid rgba(255,107,157,0.15);
    padding: 32px 28px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(196,75,255,0.06);
    transition: box-shadow 0.3s ease;
}
.card:hover {
    box-shadow: 0 12px 40px rgba(196,75,255,0.12);
}
.card-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1a1a2e;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Input Fields ── */
div[data-baseweb="base-input"],
div[data-baseweb="input"],
.stTextInput > div > div,
.stTextInput > div,
.stTextArea > div > div,
.stTextArea > div {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #FAFAFA !important;
    border: 1.5px solid #2d2d2d !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    color: #1a1a2e !important;
    font-size: 15px !important;
    font-family: 'Inter', sans-serif !important;
    caret-color: #FF6B9D !important;
    transition: all 0.25s ease !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #FF6B9D !important;
    background: #FFFFFF !important;
    box-shadow: 0 0 0 3px rgba(255,107,157,0.12) !important;
    outline: none !important;
}
.stTextInput label p,
.stTextArea label p,
.stFileUploader label p {
    color: #1a1a2e !important;
    font-weight: 700 !important;
    font-size: 17px !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    margin-bottom: 6px !important;
}

/* ── File Uploader ── */
.stFileUploader,
.stFileUploader > div,
.stFileUploader > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.stFileUploader section,
[data-testid="stFileUploadDropzone"] {
    background-color: #FAFAFA !important;
    border: 1.5px solid #2d2d2d !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    transition: all 0.25s ease !important;
}
.stFileUploader section:hover,
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #FF6B9D !important;
    background: #FFF5FB !important;
}
.stFileUploader section *,
[data-testid="stFileUploadDropzone"] * {
    color: #1a1a2e !important;
}

/* ── Analyze Button ── */
div.stButton > button {
    background: linear-gradient(135deg, #FF6B9D 0%, #C44BFF 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    letter-spacing: 0.5px !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 16px 40px !important;
    width: 100% !important;
    box-shadow: 0 8px 25px rgba(196,75,255,0.35) !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}
div.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 14px 35px rgba(196,75,255,0.45) !important;
}
div.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Result Card ── */
.result-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,245,251,0.95));
    border-radius: 20px;
    border: 1px solid rgba(255,107,157,0.2);
    padding: 36px 32px;
    box-shadow: 0 12px 40px rgba(196,75,255,0.1);
    margin-top: 20px;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: rgba(255,255,255,0.6);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid rgba(255,107,157,0.15);
    gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: #6b6b8a !important;
    padding: 8px 16px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #FF6B9D, #C44BFF) !important;
    color: white !important;
}

/* ── Success/Warning ── */
.stSuccess, .stWarning, .stError {
    border-radius: 12px !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #FF6B9D !important;
}

/* ── Floating Stickers ── */
.stickers-wrap {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.sk {
    position: absolute;
    font-size: 38px;
    opacity: 0.55;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.08));
    animation: floatUp 5s ease-in-out infinite;
}
.sk:nth-child(1)  { top: 20%; left: 17%; animation-delay: 0s;   }  /* LEFT  */
.sk:nth-child(2)  { top: 58%; left: 17%; animation-delay: 1.5s; }  /* LEFT  */
.sk:nth-child(3)  { top: 20%; right: 3%; animation-delay: 0.8s; }  /* RIGHT */
.sk:nth-child(4)  { top: 60%; right: 3%; animation-delay: 2s;   }  /* RIGHT */
.sk:nth-child(5)  { display: none; }
.sk:nth-child(6)  { display: none; }
.sk:nth-child(7)  { display: none; }
@keyframes floatUp {
    0%   { transform: translateY(0px)   rotate(0deg); }
    50%  { transform: translateY(-18px) rotate(6deg); }
    100% { transform: translateY(0px)   rotate(0deg); }
}

/* ── Divider ── */
.fancy-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #FF6B9D, #C44BFF, transparent);
    border: none;
    border-radius: 2px;
    margin: 28px 0;
}
/* ── Browse Files Button Fix ── */
[data-testid="stFileUploaderDropzoneInstructions"] button,
[data-testid="stFileUploadDropzone"] button,
.stFileUploader button {
    background: linear-gradient(135deg, #FF6B9D, #C44BFF) !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}
/* ── Status bars text ── */
[data-testid="stStatusWidget"] *,
[data-testid="stStatus"] *,
.stStatus *, .stStatus {
    color: #1a1a2e !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FLOATING STICKERS
# ─────────────────────────────────────────────
st.markdown("""
<div class="stickers-wrap">
    <span class="sk">🧴</span>
    <span class="sk">💊</span>
    <span class="sk">🌿</span>
    <span class="sk">✨</span>
    <span class="sk">🧪</span>
    <span class="sk">💧</span>
    <span class="sk">☀️</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✨ AI Skincare")
    st.markdown("---")

    st.markdown("### 📖 About This App")
    st.markdown("""
    This AI-powered skincare consultant analyzes your skin condition and provides a **personalized daily routine** backed by:
    - 📚 A clinical dermatology e-book
    - 🛍️ 1100+ real product database
    - 🇪🇬 Egyptian local alternatives
    - 🧬 Medical knowledge base
    """)

    st.markdown("---")
    st.markdown("### ⚠️ Disclaimer")
    st.markdown("""
    > This app provides **AI-generated suggestions only** and is **not a substitute for professional medical diagnosis** or treatment.
    > Always consult a licensed dermatologist for serious skin conditions.
    """)

    st.markdown("---")
    st.markdown("### 📬 Contact")
    st.markdown("""
    **Developer:** Merna Mohamed  
    **Course:** Orange Digital Center  
    **Project:** Final Year AI Project  
    """)

    st.markdown("---")
    st.markdown("<p style='font-size:11px; color:#888; text-align:center;'>Powered by Google Gemini 2.5 Flash</p>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
kb_text = load_knowledge_base()
df_products = load_products()
df_kaggle = load_csv_data("data/kaggle_data/skincare_products_clean.csv")
df_dupes = load_csv_data("data/egyptian_local_dupes.csv")


# ─────────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; margin: 20px 0 40px 0;">
    <h1 style="color: #FF6B9D; font-size: 3rem; font-weight: 800; margin-bottom: 5px; letter-spacing: -1px;">✨ AI Skincare Consultant</h1>
    <p style="color: #6b6b8a; font-size: 1.2rem; font-weight: 500;">Your Personal Dermatologist 🌸</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INPUT CARD
# ─────────────────────────────────────────────

patient_name = st.text_input("🌸 Patient Name", placeholder="e.g. Sara Ahmed")
user_description = st.text_area(
    "📝 Describe Your Skin Concern",
    placeholder="e.g. I have oily skin with acne on the forehead, sensitive to sunlight...",
    height=120
)

uploaded_file = st.file_uploader(
    "📸 Upload Clinical Image (Optional)",
    type=["jpg", "jpeg", "png"]
)


# ─────────────────────────────────────────────
# ANALYZE BUTTON
# ─────────────────────────────────────────────
col_l, col_m, col_r = st.columns([1, 3, 1])
with col_m:
    submit_clicked = st.button("✨ Analyze Skin & Generate Routine ✨", use_container_width=True)


# ─────────────────────────────────────────────
# VALIDATION & AI CALL
# ─────────────────────────────────────────────
if submit_clicked:
    if not patient_name:
        st.warning("⚠️ Please enter the patient's name to generate the prescription.")
    elif not user_description and not uploaded_file:
        st.warning("⚠️ Please enter a skin description or upload an image of the skin.")
    else:
        with st.spinner("🔬 Multi-Agent System is orchestrating 3 AI Agents..."):
            try:
                medical_book = get_uploaded_book()

                # ── AGENT 1: SKIN ANALYST ──
                with st.status("🕵️ Agent 1: Analyzing Skin Condition...") as s1:
                    prompt1 = f"""You are a Skin Analysis Agent. Your ONLY job is to analyze the patient's skin.
Patient: {patient_name}. Description: {user_description if user_description else "Image only."}.
Medical Rules: {kb_text}
Output a detailed clinical skin analysis in English."""
                    inputs1 = [prompt1]
                    if uploaded_file:
                        inputs1.append(PIL.Image.open(uploaded_file).convert("RGB"))
                    skin_analysis = model.generate_content(inputs1).text
                    s1.update(label="✅ Agent 1: Skin Analysis Complete", state="complete")

                # ── AGENT 2: PRODUCT RESEARCHER ──
                with st.status("🛍️ Agent 2: Searching Products & Local Alternatives...") as s2:
                    prompt2 = f"""You are a Skincare Product Researcher Agent.
Based on this analysis: {skin_analysis}
Find the best products from:
- Products DB: {df_products.to_csv(index=False) if df_products is not None else ""}
- Egyptian Dupes DB: {df_dupes.to_csv(index=False) if df_dupes is not None else ""}
- Kaggle DB: {df_kaggle.head(30).to_csv(index=False) if df_kaggle is not None else ""}
List recommended products with ingredients and prices in English."""
                    products_result = model.generate_content([prompt2]).text
                    s2.update(label="✅ Agent 2: Product Research Complete", state="complete")

                # ── AGENT 3: ROUTINE PLANNER ──
                with st.status("✍️ Agent 3: Writing Personalized Routine...") as s3:
                    prompt3 = f"""You are a Medical Routine Planner Agent.
Write a complete English report for {patient_name} using:
1. Skin Analysis: {skin_analysis}
2. Products: {products_result}
Structure:
## 🔍 Skin Analysis
## 💊 Recommended Ingredients
## ☀️ Morning Routine
## 🌙 Night Routine
## 🛍️ Recommended Products
## ⛔ What to Avoid
## 💡 Healing Tips"""
                    final_routine = model.generate_content([prompt3]).text
                    s3.update(label="✅ Agent 3: Report Ready", state="complete")

                try:
                    final_routine = final_routine
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "quota" in error_msg.lower():
                        st.error("⚠️ API Quota Exceeded: Your Gemini free tier limit has been reached. Please wait a minute and try again.")
                    else:
                        st.error(f"⚠️ Error generating response: {error_msg}")
                    final_routine = None

                if final_routine:
                    # ── Result Section ──
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown(f"### 📋 Personalized Report for **{patient_name}**")
                    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

                    tab1, tab2, tab3, tab4 = st.tabs([
                        "🔍 Analysis & Routine",
                        "🛍️ Products",
                        "⛔ What to Avoid",
                        "💡 Healing Tips"
                    ])

                    import re
                    def get_sec(keyword):
                        # Split only on lines starting with exactly "## "
                        parts = re.split(r'\n##\s+', "\n" + final_routine)
                        for p in parts:
                            p = p.strip()
                            if not p: continue
                            lines = p.split('\n')
                            if keyword.lower() in lines[0].lower():
                                return "\n".join(lines[1:]).strip()
                        return ""

                    prod_text = get_sec("Products") or get_sec("Recommended Products")
                    avoid_text = get_sec("Avoid") or get_sec("What to Avoid")
                    tips_text = get_sec("Healing") or get_sec("Healing Tips")

                    with tab1:
                        st.markdown(final_routine)

                    with tab2:
                        if prod_text: st.markdown(prod_text)
                        else: st.info("See the **Products** section in the full report above (Analysis & Routine tab).")

                    with tab3:
                        if avoid_text: st.markdown(avoid_text)
                        else: st.info("See the **What to Avoid** section in the full report above.")

                    with tab4:
                        if tips_text: st.markdown(tips_text)
                        else: st.info("See the **Healing Tips** section in the full report above.")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # ── Automated Actions ──
                    st.markdown("---")
                    with st.spinner("⚙️ Executing automated actions..."):
                        success, filename = save_prescription(patient_name, final_routine)
                        if success:
                            st.success(f"✅ **Action 1:** Prescription automatically saved to `prescriptions/` folder.")
                        else:
                            st.error("❌ Failed to save prescription.")

                        log_patient_data(patient_name, user_description, bool(uploaded_file))
                        st.success("✅ **Action 2:** Patient data logged to `patients_log.csv` database.")

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")

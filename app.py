import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER

# --- 1. Load Environment Variables & Configure API ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please create a .env file with GEMINI_API_KEY='YOUR_API_KEY'.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. App Configuration & Color Palettes ---
st.set_page_config(
    page_title="GlobalWell AI",
    layout="centered"
)

# Color palettes
PALETTE_LIGHT = {
    "BG": "#F0F2F6", "BG_GRADIENT": "linear-gradient(135deg, #FFFFFF 0%, #E8EBF2 100%)",
    "TEXT": "#2B3A67", "PRIMARY": "#0057B8", "PRIMARY_HOVER": "#00418A",
    "SECONDARY": "#FFFFFF",
    "ACCENT": "#F39C12", "ACCENT_HOVER": "#D95B00",
    "DISCLAIMER_BG": "#FFFBEB", "DISCLAIMER_BORDER": "#F39C12",
    "TITLE_GRADIENT": "linear-gradient(45deg, #0057B8, #2B3A67)",
    "CHAT_AI": "#E9F0FB", "CHAT_USER": "#FFFFFF", "CARD_BG": "rgba(255, 255, 255, 0.9)",
    "BORDER": "rgba(0, 87, 184, 0.2)", "SECTION_BG": "rgba(255, 255, 255, 1)"
}
PALETTE_DARK = {
    "BG": "#17224D", "BG_GRADIENT": "linear-gradient(135deg, #17224D 0%, #233A75 100%)",
    "TEXT": "#EAECEE", "PRIMARY": "#F58125", "PRIMARY_HOVER": "#F9A359",
    "SECONDARY": "rgba(44, 81, 147, 0.5)", "ACCENT": "#5184C4", "ACCENT_HOVER": "#2C5193",
    "DISCLAIMER_BG": "#2B3A67", "DISCLAIMER_BORDER": "#F58125",
    "TITLE_GRADIENT": "linear-gradient(45deg, #F58125, #FFFFFF)",
    "CHAT_AI": "#2C5193", "CHAT_USER": "#17224D", "CARD_BG": "rgba(44, 81, 147, 0.4)",
    "BORDER": "rgba(245, 129, 37, 0.4)", "SECTION_BG": "rgba(44, 81, 147, 0.6)"
}

# --- 3. UI Setup & Styling ---
st.sidebar.header("GlobalWell AI")
st.sidebar.markdown("Your personal wellness companion.")
st.sidebar.markdown("---")
st.sidebar.subheader("Theme Settings")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)
PALETTE = PALETTE_DARK if dark_mode else PALETTE_LIGHT

# Conditionally set a background for the toggle in light mode
toggle_bg_color = 'rgba(0, 87, 184, 0.1)' if not dark_mode else 'transparent'

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    /* --- Base & Typography --- */
    .stApp {{
        background: {PALETTE["BG_GRADIENT"]};
        color: {PALETTE["TEXT"]};
        font-family: 'Inter', sans-serif;
    }}

    h1 {{ font-size: 3.2rem; font-weight: 800; text-align: center; padding: 1rem 0 1.5rem 0; background: {PALETTE["TITLE_GRADIENT"]}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    h3 {{ color: {PALETTE["TEXT"]}; font-weight: 700; margin-top: 1.5rem; }}

    /* --- Sidebar Styling --- */
    section[data-testid="stSidebar"] {{
        background: {PALETTE["SECONDARY"]};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }}

    /* --- Sidebar Text & Widget Color --- */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {{
        color: {PALETTE["TEXT"]} !important;
    }}

    /* --- ✅ FIX FOR TOGGLE VISIBILITY IN LIGHT MODE --- */
    section[data-testid="stSidebar"] div[data-testid="stToggle"] {{
        background-color: {toggle_bg_color};
        border-radius: 15px;
        padding: 4px 10px;
        margin-top: 5px;
        transition: background-color 0.3s ease;
    }}

    /* --- Layout & Cards (Glassmorphism) --- */
    .card {{
        background: {PALETTE["CARD_BG"]};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 1.5rem;
        border: 1px solid {PALETTE["BORDER"]};
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    }}

    /* --- Wellness Plan Section Boxes --- */
    .section-box {{
        background: {PALETTE["SECTION_BG"]};
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid {PALETTE["BORDER"]};
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}
    .section-box:last-child {{ margin-bottom: 0; }}
    .section-box h2 {{
        color: {PALETTE["PRIMARY"]};
        border-bottom: 2px solid {PALETTE["BORDER"]};
        font-size: 1.5rem;
        margin-top: 0;
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
    }}
    .disclaimer-box {{
        background-color: {PALETTE["DISCLAIMER_BG"]};
        border-left: 5px solid {PALETTE["DISCLAIMER_BORDER"]};
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        color: {PALETTE["TEXT"]};
        font-size: 14px;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }}

    /* --- Buttons & Inputs --- */
    div[data-testid="stButton"] > button {{ background: linear-gradient(45deg, {PALETTE["PRIMARY"]}, {PALETTE["PRIMARY_HOVER"]}); color: white; border-radius: 10px; padding: 14px 28px; font-weight: 700; font-size: 16px; border: none; transition: all 0.3s ease-in-out; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); }}
    div[data-testid="stButton"] > button:hover {{ transform: scale(1.05) translateY(-2px); box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25); }}
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {{
        border: 1px solid {PALETTE["BORDER"]};
        transition: all 0.2s ease-in-out !important;
    }}
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {{
        border: 1px solid {PALETTE["PRIMARY"]};
        box-shadow: 0 0 0 2px {PALETTE["BORDER"]};
    }}

    /* --- Custom Styled Tabs --- */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {{
        background-color: transparent;
        border-bottom: 2px solid transparent;
        color: {PALETTE["TEXT"]};
        transition: all 0.2s ease-in-out;
        padding: 0.8rem 1.2rem;
        border-radius: 8px 8px 0 0;
    }}
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
        background-color: {PALETTE["CARD_BG"]};
        border-bottom: 2px solid {PALETTE["ACCENT"]};
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        border-bottom: 2px solid {PALETTE["PRIMARY"]};
        background-color: {PALETTE["CARD_BG"]};
    }}

    /* --- Tools & Animations --- */
    .breathing-circle {{ width: 150px; height: 150px; background: linear-gradient(135deg, {PALETTE["PRIMARY"]}, {PALETTE["ACCENT"]}); border-radius: 50%; margin: 2rem auto; display: flex; align-items: center; justify-content: center; animation: breathe 5s ease-in-out infinite; box-shadow: 0 0 30px {PALETTE["PRIMARY"]}; }}
    @keyframes breathe {{ 0%, 100% {{ transform: scale(0.95); box-shadow: 0 0 20px {PALETTE["BORDER"]}; }} 50% {{ transform: scale(1.05); box-shadow: 0 0 40px {PALETTE["PRIMARY"]}; }} }}
    .breathing-text {{ color: white; font-weight: bold; font-size: 1.2rem; }}
</style>
""", unsafe_allow_html=True)

# --- 4. Helper Functions ---
def sanitize_input(text):
    if not text: return ""
    return re.sub(r'[\*_`]', '', text).strip()

def generate_plan_pdf(plan_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles['h1'].alignment = TA_CENTER
    story = [Paragraph("Your Personalized Wellness Plan", styles['h1']), Spacer(1, 24)]
    plan_text = plan_text.replace('###', '').replace('**', '')
    for line in plan_text.split('\n'):
        if line.startswith('## '): story.append(Paragraph(line.replace('## ', ''), styles['h2']))
        else: story.append(Paragraph(line, styles['Normal']))
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_ai_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An API error occurred: {e}")
        return None

def get_wellness_plan_prompt(inputs):
    return f"""
    You are GlobalWell AI, an empathetic AI Wellness Buddy. Your mission is to provide a personalized, actionable wellness plan that strongly aligns with **UN SDG 3: Good Health and Well-being**.
    **Core Instructions:**
    1.  **Prioritize Accessibility & Affordability:** All suggestions must be practical, low-cost, and accessible. Recommend locally available, seasonal foods. For fitness, prioritize activities that require little to no equipment.
    2.  **Holistic Approach:** Cover nutrition, physical activity, mental well-being, and sleep.
    3.  **Content Restriction:** Absolutely NO suggestions of specific supplements, medicines, or drugs.
    4.  **SDG 3 Section:** Include a dedicated section titled "**Alignment with SDG 3**" explaining how the plan supports accessible, preventative, and holistic health.
    **User Profile:**
    - Location: {inputs['region']}, {inputs['state']}, {inputs['country']} | Age: {inputs['age']}, Gender: {inputs['gender']} | Diet: {inputs['diet']}, Activity: {inputs['activity']} | Health Conditions: {inputs['health'] or 'None'} | Goal: {inputs['goal']} | Reason: {inputs['reason'] or 'Not specified'}
    """

def get_local_info_prompt(location):
    return f"""
    As GlobalWell AI, provide two pieces of information for a user in **{location}**, focusing on UN SDG 3 principles (accessibility, affordability):
    1.  **Hyper-Local Produce Guide:** List 3-4 seasonal, affordable, and nutritious fruits or vegetables readily available in local markets there right now.
    2.  **Wellness Myth Buster:** Present one common, relevant "Myth vs. Fact" about health, debunking an expensive trend and promoting a simple, evidence-based alternative.
    Format this clearly with markdown.
    """

# --- 5. Streamlit App Layout ---
if 'wellness_plan' not in st.session_state: st.session_state.wellness_plan = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'local_info' not in st.session_state: st.session_state.local_info = None

st.title("GlobalWell AI")
st.markdown("Your AI guide to a healthier lifestyle, aligned with **UN SDG 3: Good Health and Well-being**.")

with st.sidebar:
    st.markdown("---")
    st.subheader("Your Profile")
    user_inputs = {
        'country': st.text_input("Country", "India"), 'state': st.text_input("State/Province", "Gujarat"),
        'region': st.text_input("City/Region", "Bharuch"), 'age': st.slider("Age", 1, 100, 30),
        'gender': st.radio("Gender", ["Male", "Female", "Other"]), 'diet': st.selectbox("Dietary Preference", ["Omnivore", "Vegetarian", "Vegan"]),
        'activity': st.selectbox("Activity Level", ["Low", "Medium", "High"]),
        'health': sanitize_input(st.text_input("Existing Health Conditions (Optional)")),
    }

st.header("Your Wellness Goal")
user_inputs['goal'] = sanitize_input(st.text_area("What is your main wellness goal?", height=100))
user_inputs['reason'] = sanitize_input(st.text_area("Any specific context or reason for this goal? (Optional)", height=70))


if st.button("Generate My Wellness Plan"):
    if not user_inputs['goal']:
        st.warning("Please specify your wellness goal.")
    else:
        with st.spinner("Crafting your unique plan..."):
            prompt = get_wellness_plan_prompt(user_inputs)
            plan = generate_ai_response(prompt)
            if plan:
                st.session_state.wellness_plan = plan
                st.session_state.chat_history = []
                st.session_state.local_info = None

if st.session_state.wellness_plan:
    tab1, tab2, tab3 = st.tabs(["Your Wellness Plan", "Local Wellness & Tools", "Chat About Your Plan"])

    with tab1:
        st.markdown(f"""<div class="disclaimer-box"><strong>Disclaimer:</strong> This is not medical advice. Always consult a healthcare professional.</div>""", unsafe_allow_html=True)
        
        plan_text = st.session_state.wellness_plan
        sections = re.split(r'\n(?=## )', plan_text)
        
        for section in sections:
            st.markdown(f'<div class="section-box">{section}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_buffer = generate_plan_pdf(st.session_state.wellness_plan)
        st.download_button("Download Plan as PDF", data=pdf_buffer, file_name="GlobalWell_AI_Plan.pdf", mime="application/pdf")

    with tab2:
        st.subheader("Mental Well-being Tool")
        st.markdown("Take a moment to center yourself with this simple breathing exercise.")
        st.markdown('<div class="breathing-circle"><div class="breathing-text">Breathe</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Health Literacy Hub")
        if st.button("Get Local Wellness Info"):
            with st.spinner("Finding local insights..."):
                location = f"{user_inputs['region']}, {user_inputs['country']}"
                prompt = get_local_info_prompt(location)
                st.session_state.local_info = generate_ai_response(prompt)
        if st.session_state.local_info:
            st.markdown(st.session_state.local_info)
        
    with tab3:
        for msg in st.session_state.chat_history:
            bubble_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
            st.markdown(f'<div class="chat-bubble {bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        
        question = st.text_area("Have a question about your plan?", key="chat_input")
        if st.button("Ask Question"):
            if question:
                st.session_state.chat_history.append({"role": "user", "content": question})
                with st.spinner("Thinking..."):
                    prompt = f"Based on this plan:\n{st.session_state.wellness_plan}\n\nUser question: {question}\nAnswer:"
                    answer = generate_ai_response(prompt)
                    st.session_state.chat_history.append({"role": "ai", "content": answer})
                st.rerun()

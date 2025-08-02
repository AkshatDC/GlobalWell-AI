import streamlit as st
import os
from dotenv import load_dotenv

from config.theme import PALETTE_LIGHT, PALETTE_DARK
from utils.helpers import sanitize_input
from services.ai_service import generate_ai_response
from services.pdf_service import generate_plan_pdf
from utils.prompts import get_wellness_plan_prompt, get_local_info_prompt
from components.ui_components import setup_sidebar, apply_custom_styles, breathing_circle

# --- Load Environment Variables ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please add it to your .env file.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(page_title="GlobalWell AI", layout="centered")

# --- Sidebar Setup ---
dark_mode, user_inputs = setup_sidebar()
PALETTE = PALETTE_DARK if dark_mode else PALETTE_LIGHT
apply_custom_styles(PALETTE, dark_mode)

# --- Initialize Session State ---
if 'wellness_plan' not in st.session_state:
    st.session_state.wellness_plan = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'local_info' not in st.session_state:
    st.session_state.local_info = None

# --- Main Content ---
st.title("GlobalWell AI")
st.markdown("Your AI guide to a healthier lifestyle, aligned with **UN SDG 3: Good Health and Well-being**.")

st.header("Your Wellness Goal")
user_inputs['goal'] = sanitize_input(st.text_area("What is your main wellness goal?", height=100))
user_inputs['reason'] = sanitize_input(st.text_area("Any specific context or reason for this goal? (Optional)", height=70))

# --- Generate Wellness Plan ---
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

# --- Display Wellness Plan & Tools ---
if st.session_state.wellness_plan:
    tab1, tab2, tab3 = st.tabs(["Your Wellness Plan", "Local Wellness & Tools", "Chat About Your Plan"])

    with tab1:
        st.markdown("""<div class="disclaimer-box"><strong>Disclaimer:</strong> This is not medical advice. Always consult a healthcare professional.</div>""", unsafe_allow_html=True)
        sections = st.session_state.wellness_plan.split('\n## ')
        for idx, section in enumerate(sections):
            if idx == 0 and not section.startswith('## '):
                section = '## ' + section
            st.markdown(f'<div class="section-box">{section}</div>', unsafe_allow_html=True)

        pdf_buffer = generate_plan_pdf(st.session_state.wellness_plan)
        st.download_button("Download Plan as PDF", data=pdf_buffer, file_name="GlobalWell_AI_Plan.pdf", mime="application/pdf")

    with tab2:
        st.subheader("Mental Well-being Tool")
        breathing_circle()
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
            role_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
            st.markdown(f'<div class="chat-bubble {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

        question = st.text_area("Have a question about your plan?", key="chat_input")
        if st.button("Ask Question"):
            if question.strip():
                st.session_state.chat_history.append({"role": "user", "content": question})
                with st.spinner("Thinking..."):
                    prompt = f"Based on this plan:\n{st.session_state.wellness_plan}\n\nUser question: {question}\nAnswer:"
                    answer = generate_ai_response(prompt)
                    st.session_state.chat_history.append({"role": "ai", "content": answer})
                st.rerun()

import streamlit as st

def setup_sidebar():
    st.sidebar.header("GlobalWell AI")
    st.sidebar.markdown("Your personal wellness companion.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Theme Settings")
    dark_mode = st.sidebar.toggle("Dark Mode", value=True)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Your Profile")
    user_inputs = {
        'country': st.text_input("Country", "India"), 'state': st.text_input("State/Province", "Gujarat"),
        'region': st.text_input("City/Region", "Bharuch"), 'age': st.slider("Age", 1, 100, 30),
        'gender': st.radio("Gender", ["Male", "Female", "Other"]), 'diet': st.selectbox("Dietary Preference", ["Omnivore", "Vegetarian", "Vegan"]),
        'activity': st.selectbox("Activity Level", ["Low", "Medium", "High"]),
        'health': st.text_input("Existing Health Conditions (Optional)")
    }
    return dark_mode, user_inputs

def apply_custom_styles(PALETTE):
    with open("static/custom_styles.css", "r") as f:
        css = f.read()
        for key, value in PALETTE.items():
            css = css.replace(f"{{{{{key}}}}}", value)
        toggle_bg = 'rgba(0, 87, 184, 0.1)' if PALETTE == PALETTE_LIGHT else 'transparent'
        css = css.replace("{{TOGGLE_BG}}", toggle_bg)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

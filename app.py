import sys
import subprocess
# --- 0. Package Installation ---
try:
    import streamlit as st
    import google.generativeai as genai
    from dotenv import load_dotenv
    from reportlab.lib.pagesizes import letter
except ImportError:
    import streamlit as st
    st.info("First-time setup: Installing required packages... Please wait a moment.")
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                          "streamlit", "google-generativeai", "python-dotenv", "reportlab"])
    st.success("Packages installed successfully! The app is now restarting.")
    st.rerun()


import streamlit as st
import google.generativeai as genai
import os, re, time, datetime, random, base64
from dotenv import load_dotenv
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from streamlit.components.v1 import html


# --- Helper functions (must be defined before use) ---
def sanitize_input(text):
    if not text:
        return ""
    return re.sub(r'[\\*_]', '', text).strip()


def generate_plan_pdf(plan_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles['h1'].alignment = TA_CENTER
    story = [Paragraph("Your Personalized Wellness Plan", styles['h1']), Spacer(1, 24)]
    plan_text = plan_text.replace('###', '').replace('**', '')
    for line in plan_text.split('\n'):
        if line.startswith('## '):
            story.append(Paragraph(line.replace('## ', ''), styles['h2']))
        else:
            story.append(Paragraph(line, styles['Normal']))
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
You are GlobalWell AI, an empathetic AI Wellness Buddy. Provide a personalized, actionable wellness plan that aligns with **UN SDG 3**.


**Core Instructions:**
1. Accessibility & Affordability: Practical, low-cost, seasonal foods; minimal-equipment fitness.
2. Holistic: Cover nutrition, physical activity, mental well-being, and sleep.
3. Restriction: No specific supplements/medicines/drugs.
4. Add a section: **Alignment with SDG 3**.


**User Profile:**
- Location: {inputs['region']}, {inputs['state']}, {inputs['country']} | Age: {inputs['age']}, Gender: {inputs['gender']}
- Diet: {inputs['diet']}, Activity: {inputs['activity']} | Health Conditions: {inputs['health'] or 'None'}
- Goal: {inputs['goal']} | Reason: {inputs['reason'] or 'Not specified'}
"""


def get_local_info_prompt(location):
    return f"""
As GlobalWell AI, for a user in **{location}**:
1. **Hyper-Local Produce Guide:** List 3–4 seasonal, affordable, nutritious fruits/vegetables readily available now.
2. **Wellness Myth Buster:** One relevant "Myth vs. Fact" debunking an expensive trend with a simple alternative.
Format clearly with markdown.
"""


# --- Tighten spacing above title and global styles, remove space above main title ---
st.markdown("""
    <style>
    .block-container {padding-top: 0rem !important;}
    h1 {margin-top: 0 !important;}
    /* Sidebar text color in dark mode */
    section[data-testid="stSidebar"] * {
      color: #EAECEE !important;
    }
    /* Button container fix */
    .sidebar-button-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 10px;
    }
    .sidebar-button-row > div {
        flex: 1 1 0px;
    }
    /* Fix text color for cards and section boxes in dark mode */
    .section-box, .card {
        color: #EAECEE !important;
        background: rgba(44, 81, 147, 0.5) !important;
    }
    /* Additional global dark mode styling */
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        color: #EAECEE !important;
        background-color: #17224D !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- 1. Load API ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please create a .env file with GEMINI_API_KEY='YOUR_API_KEY'.")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


# --- 2. App Config & Color Palette ---
st.set_page_config(
    page_title="GlobalWell AI",
    layout="centered",
    initial_sidebar_state="expanded"
)


PALETTE_DARK = {
    "BG": "#17224D",
    "BG_GRADIENT": "linear-gradient(135deg, #17224D 0%, #233A75 100%)",
    "TEXT": "#EAECEE",
    "PRIMARY": "#F58125",
    "PRIMARY_HOVER": "#F9A359",
    "SECONDARY": "rgba(44, 81, 147, 0.5)",
    "ACCENT": "#5184C4",
    "ACCENT_HOVER": "#2C5193",
    "DISCLAIMER_BG": "#2B3A67",
    "DISCLAIMER_BORDER": "#F58125",
    "TITLE_GRADIENT": "linear-gradient(45deg, #F58125, #FFFFFF)",
    "CHAT_AI": "#2C5193",
    "CHAT_USER": "#17224D",
    "CARD_BG": "rgba(44, 81, 147, 0.4)",
    "BORDER": "rgba(245, 129, 37, 0.4)",
    "SECTION_BG": "rgba(44, 81, 147, 0.6)"
}


PALETTE = PALETTE_DARK  # Dark mode only


# --- 3. Session State Defaults ---
defaults = {
    'wellness_plan': None,
    'chat_history': [],
    'local_info': None,
    'gratitude': {},
    'last_hydration': time.time(),
    'daily_tip': None,
    'noise_playing': False,
    'noise_bytes': None,
    'noise_choice': "White Noise",
    'chime_playing': False,
    'chime_duration_sec': 10,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# --- 4. Sidebar ---
st.sidebar.header("GlobalWell AI")
st.sidebar.markdown("Your personal wellness companion.")
st.sidebar.markdown("---")


def load_audio_file(filepath):
    with open(filepath, 'rb') as f:
        return f.read()


NOISE_OPTIONS = {
    "White Noise": "E:/GLobalWell/white-noise-358382.mp3",
    "Rain": "E:/GLobalWell/calming-rain-257596.mp3",
    "Brown Noise": "E:/GLobalWell/soft-brown-noise-299934.mp3"
}


noise_choice = st.sidebar.selectbox("Select Ambient Noise", list(NOISE_OPTIONS.keys()), index=list(NOISE_OPTIONS.keys()).index(st.session_state.noise_choice) if st.session_state.noise_choice in NOISE_OPTIONS else 0)
st.session_state.noise_choice = noise_choice

noise_col1, noise_col2 = st.sidebar.columns(2)
with noise_col1:
    start_noise = st.button("Start Noise", key="noise_start_btn")
with noise_col2:
    stop_noise = st.button("Stop Noise", key="noise_stop_btn")

def get_audio_base64(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

if start_noise:
    try:
        base64_audio = get_audio_base64(NOISE_OPTIONS[noise_choice])
        st.session_state.noise_bytes = base64_audio
        st.session_state.noise_playing = True
    except Exception as e:
        st.error(f"Failed to load audio file: {e}")
        st.session_state.noise_playing = False

if stop_noise:
    st.session_state.noise_playing = False

if st.session_state.noise_playing and st.session_state.noise_bytes:
    audio_html = f"""
    <audio controls autoplay loop style="width:100%">
        <source src="data:audio/mp3;base64,{st.session_state.noise_bytes}" type="audio/mp3" />
        Your browser does not support the audio element.
    </audio>
    """
    st.sidebar.markdown(audio_html, unsafe_allow_html=True)
else:
    st.sidebar.markdown("<i>No ambient noise playing.</i>", unsafe_allow_html=True)


# Chime Controls with loop until stopped
chime_cols = st.sidebar.columns(2)
with chime_cols[0]:
    start_chime = st.button("Start Chime", key="chime_start_btn")
with chime_cols[1]:
    stop_chime = st.button("Stop Chime", key="chime_stop_btn")

if start_chime:
    st.session_state.chime_playing = True
if stop_chime:
    st.session_state.chime_playing = False

if st.session_state.chime_playing:
    duration = st.session_state.chime_duration_sec * 1000  # milliseconds
    chime_js = f"""
    <script>
    (function(){{
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const gainNode = ctx.createGain();
      gainNode.gain.value = 0.13;
      gainNode.connect(ctx.destination);

      let oscillator;
      function playTone() {{
        oscillator = ctx.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(660, ctx.currentTime);
        oscillator.connect(gainNode);
        oscillator.start();
        gainNode.gain.setValueAtTime(0.13, ctx.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.05, ctx.currentTime + {duration/1000 * 0.75});
        gainNode.gain.linearRampToValueAtTime(0.0, ctx.currentTime + {duration/1000});
        oscillator.stop(ctx.currentTime + {duration/1000});
        oscillator.onended = () => {{
          if(window._gwChimePlaying) {{
            playTone();
          }}
        }};
      }}
      window._gwChimePlaying = true;
      playTone();
      window.stopChime = () => {{
        window._gwChimePlaying = false;
        if (oscillator) {{
          oscillator.stop();
          oscillator.disconnect();
        }}
        gainNode.disconnect();
      }};
    }})();
    </script>
    """
    st.components.v1.html(chime_js, height=40)
else:
    st.components.v1.html("""
    <script>
    if(window.stopChime) {{
      window.stopChime();
    }}
    </script>""", height=0)


# --- 5. Global CSS ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
:root {{
  --text: {PALETTE["TEXT"]};
  --primary: {PALETTE["PRIMARY"]};
  --primaryH: {PALETTE["PRIMARY_HOVER"]};
  --accent: {PALETTE["ACCENT"]};
  --border: {PALETTE["BORDER"]};
  --card: {PALETTE["CARD_BG"]};
}}
.stApp {{
  background: {PALETTE["BG_GRADIENT"]};
  color: var(--text);
  font-family: 'Inter', sans-serif;
  transition: background-color 0.5s ease, color 0.5s ease;
}}
h1 {{
  font-size: 3.0rem;
  font-weight: 800;
  text-align: center;
  padding: 1rem 0 1.0rem 0;
  background: {PALETTE["TITLE_GRADIENT"]};
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-top: 0 !important;
  transition: color 0.5s ease;
}}
h3 {{ color: var(--text); font-weight: 700; margin-top: 1.2rem; }}

.card, .section-box {{
  background: var(--card);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  border-radius: 18px;
  padding: 1.3rem;
  border: 1px solid var(--border);
  box-shadow: 0 10px 30px 0 rgba(0,0,0,0.08);
  transition: background-color 0.5s ease, color 0.5s ease, box-shadow .15s ease;
}}
.card:hover, .section-box:hover {{
  transform: translateY(-2px);
  box-shadow: 0 14px 35px rgba(0,0,0,0.12);
}}
section[data-testid="stSidebar"] {{
  background: {PALETTE["SECONDARY"]};
  backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  border-right: 1px solid rgba(255,255,255,0.15);
  transition: background-color 0.5s ease, color 0.5s ease;
}}
section[data-testid="stSidebar"] * {{ color: {PALETTE["TEXT"]} !important; }}

div[data-testid="stButton"] > button {{
  background: linear-gradient(45deg, var(--primary), var(--primaryH));
  color: white; border-radius: 12px; padding: 12px 22px; font-weight: 700; border: none;
  transition: transform .2s ease, box-shadow .2s ease;
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}}
div[data-testid="stButton"] > button:hover {{
  transform: scale(1.03) translateY(-1px); box-shadow: 0 10px 28px rgba(0,0,0,0.25);
}}

div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {{
  border: 1px solid var(--border);
  transition: all .2s ease-in-out !important;
  color: var(--text) !important;
  background-color: #17224D !important;
}}
div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {{
  border: 1px solid var(--primary);
  box-shadow: 0 0 0 2px var(--border);
}}

div[data-testid="stTabs"] button[data-baseweb="tab"] {{
  background-color: transparent; border-bottom: 2px solid transparent; color: var(--text);
  transition: all .2s ease-in-out; padding: .8rem 1.2rem; border-radius: 10px 10px 0 0;
}}
div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
  background-color: {PALETTE["CARD_BG"]}; border-bottom: 2px solid {PALETTE["ACCENT"]};
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
  border-bottom: 2px solid var(--primary); background-color: {PALETTE["CARD_BG"]};
}}
.disclaimer-box {{
  background-color: {PALETTE["DISCLAIMER_BG"]};
  border-left: 5px solid {PALETTE["DISCLAIMER_BORDER"]};
  padding: 1rem 1.4rem; border-radius: 10px; margin-bottom: 1.3rem; color: var(--text); font-size: 14px;
}}
.breathing-circle {{
  width: 160px; height: 160px; border-radius: 50%;
  background: linear-gradient(135deg, {PALETTE["PRIMARY"]}, {PALETTE["ACCENT"]});
  margin: 1.2rem auto; display: flex; align-items: center; justify-content: center;
  animation-name: breathe; animation-timing-function: ease-in-out; animation-iteration-count: infinite;
  box-shadow: 0 0 30px {PALETTE["PRIMARY"]};
}}
.breathing-circle.work {{ animation-duration: 5s; }}
.breathing-circle.break {{ animation-duration: 8s; }}
@keyframes breathe {{
  0%, 100% {{ transform: scale(0.94); box-shadow: 0 0 18px var(--border); }}
  50% {{ transform: scale(1.06); box-shadow: 0 0 42px var(--primary); }}
}}
.breathing-text {{ color: white; font-weight: 800; font-size: 1.1rem; letter-spacing: .6px; }}

</style>
""", unsafe_allow_html=True)


# --- Main App Content ---


st.title("GlobalWell AI")
st.markdown("Your AI guide to a healthier lifestyle, aligned with **UN SDG 3: Good Health and Well-being**.")


DAILY_TIPS = [
    "A 5-minute walk after meals helps stabilize energy.",
    "Stack habits: tie water sips to app switches or calls.",
    "Slow your exhale: 4-in / 6-out reduces stress fast.",
    "Keep fruit visible; you’ll eat it more.",
    "Protect sleep: same wake-up time every day."
]
if not st.session_state.daily_tip:
    st.session_state.daily_tip = DAILY_TIPS[int(time.time()) % len(DAILY_TIPS)]


st.markdown(f"""
<div class="card" style="display:flex;align-items:center;gap:.8rem;">
  <div style="font-size:1.2rem;">💡 <b>Daily Tip:</b> {st.session_state.daily_tip}</div>
</div>
""", unsafe_allow_html=True)


user_inputs = {
    'country': st.sidebar.text_input("Country", "India"),
    'state': st.sidebar.text_input("State/Province", "Gujarat"),
    'region': st.sidebar.text_input("City/Region", "Bharuch"),
    'age': st.sidebar.slider("Age", 1, 100, 30),
    'gender': st.sidebar.radio("Gender", ["Male", "Female", "Other"], horizontal=True),
    'diet': st.sidebar.selectbox("Dietary Preference", ["Omnivore", "Pescatarian", "Vegetarian", "Vegan"]),
    'activity': st.sidebar.selectbox("Activity Level", ["Low", "Medium", "High"]),
    'health': sanitize_input(st.sidebar.text_input("Existing Health Conditions (Optional)")),
}


st.header("Your Wellness Goal")
user_inputs['goal'] = sanitize_input(st.text_area("What is your main wellness goal?", height=100))
user_inputs['reason'] = sanitize_input(st.text_area("Any specific context or reason for this goal? (Optional)", height=70))


gen_clicked = st.button("Generate My Wellness Plan", use_container_width=True)


if gen_clicked:
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
                st.balloons()


tab1, tab2, tab3 = st.tabs(["Your Wellness Plan", "Local Wellness & Tools", "Chat About Your Plan"])


with tab1:
    if st.session_state.wellness_plan:
        st.markdown(f"""<div class="disclaimer-box"><strong>Disclaimer:</strong> This is not medical advice. Always consult a healthcare professional.</div>""", unsafe_allow_html=True)
        sections = re.split(r'\n(?=## )', st.session_state.wellness_plan)
        for section in sections:
            st.markdown(f'<div class="section-box">{section}</div>', unsafe_allow_html=True)
        pdf_buffer = generate_plan_pdf(st.session_state.wellness_plan)
        st.download_button("Download Plan as PDF", data=pdf_buffer, file_name="GlobalWell_AI_Plan.pdf", mime="application/pdf")
    else:
        st.info("Tell me your goal above, then click **Generate My Wellness Plan** to get started.")


with tab2:
    if time.time() - st.session_state.last_hydration > 2 * 60 * 60:
        st.toast("💧 Hydration reminder: take a few sips of water.", icon="💧")
        st.session_state.last_hydration = time.time()
    st.subheader("Breathing Tool + Pomodoro (Synced)")
    st.markdown("**How to use:** Start a Pomodoro session. The **breathing orb** matches the phase — calmer pace in Work, slower deep breaths in Breaks.")
    st.markdown('<div id="breathing-orb" class="breathing-circle work"><div class="breathing-text">Breathe</div></div>', unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns([1,1,1,2])
    with p1:
        work_min = st.number_input("Work (min)", min_value=1, max_value=120, value=25, step=1)
    with p2:
        break_min = st.number_input("Break (min)", min_value=1, max_value=60, value=5, step=1)
    with p3:
        rounds = st.number_input("Rounds", min_value=1, max_value=12, value=4, step=1)
    with p4:
        start_timer = st.button("Start Pomodoro")

    if start_timer:
        now = int(time.time() * 1000)
        html(f"""
            <div id="gw_timer" style="font-weight:800;font-size:22px;margin:8px 0 12px 0;">Starting...</div>
            <script>
            (function(){{{{
                const workMs = {work_min} * 60 * 1000;
                const breakMs = {break_min} * 60 * 1000;
                let rounds = {rounds};
                let phase = 'work';
                let end = Date.now() + workMs;
                const orb = document.querySelector('#breathing-orb');
                const timerEl = document.querySelector('#gw_timer');
                function setPhase(p){{{{
                    phase = p;
                    if(orb) {{
                        orb.classList.remove('work','break');
                        orb.classList.add(p);
                    }}
                }}}}
                function confetti(){{{{
                    const el = document.createElement('div');
                    el.style.cssText='position:fixed;inset:0;pointer-events:none;z-index:9999;overflow:hidden;';
                    for(let i=0;i<60;i++) {{
                        const s=document.createElement('div');
                        s.textContent='🎉';
                        s.style.position='absolute';
                        s.style.left=(Math.random()*100)+'%';
                        s.style.top='-10%';
                        s.style.fontSize=(12+Math.random()*18)+'px';
                        s.style.animation=`fall 1200ms ease-in forwards`;
                        s.style.animationDelay=(Math.random()*600)+'ms';
                        el.appendChild(s);
                    }}
                    document.body.appendChild(el);
                    setTimeout(()=>el.remove(),1600);
                }}}}
                const style = document.createElement('style');
                style.textContent='@keyframes fall{{to{{transform:translateY(120vh) rotate(720deg);opacity:.8}}}}';
                document.head.appendChild(style);
                function tick(){{{{
                    const now = Date.now();
                    let diff = Math.max(0, Math.floor((end - now)/1000));
                    const m = String(Math.floor(diff/60)).padStart(2,'0'),
                        s = String(diff%60).padStart(2,'0');
                    if(timerEl) timerEl.innerText = (phase==='work'?'🧑‍💻 Work ':'☕ Break ')+ m + ':' + s;
                    if(diff<=0) {{
                        if(phase==='work') {{
                            confetti();
                            setPhase('break');
                            end = Date.now() + breakMs;
                        }} else {{
                            rounds -= 1;
                            if(rounds <= 0) {{
                                if(timerEl) timerEl.innerText = '✅ Pomodoro Complete — great job!';
                                clearInterval(window._gwPomodoro);
                                return;
                            }}
                            setPhase('work');
                            end = Date.now() + workMs;
                        }}
                    }}
                }}}}
                setPhase('work');
                if(window._gwPomodoro) clearInterval(window._gwPomodoro);
                window._gwPomodoro = setInterval(tick, 250);
            }}}})();
            </script>
        """, height=40)
    st.markdown("---")
    with st.expander("How this helps"):
        st.markdown("""
- Pomodoro: Work in focused bursts (e.g., 25 min), then take a short break (e.g., 5 min). This reduces fatigue and improves consistency.
- Breathing Orb: In Work, keep calm attention (medium pace). In Break, breathe slower and deeper to reset stress.
- Tip: During breaks, look away from screens for 30 seconds and do 5 slow breaths following the orb.
        """)

    st.subheader("Mini Gratitude Journal")
    today_key = str(datetime.date.today())
    g1 = st.text_input("1) Something I'm grateful for", key=f"g1_{today_key}")
    g2 = st.text_input("2) Another thing I'm grateful for", key=f"g2_{today_key}")
    g3 = st.text_input("3) One small win today", key=f"g3_{today_key}")
    save_g = st.button("Save Today's Gratitude")
    if save_g:
        st.session_state.gratitude[today_key] = [g1, g2, g3]
        st.success("Saved! Come back tomorrow for more.")
    if st.session_state.gratitude:
        with st.expander("View Gratitude History"):
            for d, items in sorted(st.session_state.gratitude.items(), reverse=True):
                st.markdown(f"**{d}**")
                for i, it in enumerate(items, 1):
                    if it and it.strip():
                        st.write(f"- {i}. {it}")

    st.markdown("---")
    st.subheader("Mindfulness Fact of the Day")
    facts = [
        "Long exhale stimulates the parasympathetic (calming) response.",
        "Light morning sunlight helps anchor your body clock.",
        "Journaling for 5 minutes can reduce rumination.",
        "Walking meetings boost creativity in many small studies.",
        "A tidy desk can reduce cognitive load and decision fatigue."
    ]
    idx = int(time.time() // 86400) % len(facts)
    st.info(f"🧠 {facts[idx]}")

    st.markdown("---")
    st.subheader("Health Literacy Hub")
    if st.button("Get Local Wellness Info"):
        with st.spinner("Finding local insights..."):
            location = f"{user_inputs['region']}, {user_inputs['country']}"
            prompt = get_local_info_prompt(location)
            st.session_state.local_info = generate_ai_response(prompt)
    if st.session_state.local_info:
        st.markdown(st.session_state.local_info)

    st.markdown("---")
    st.subheader("Wellness Quick Quiz")
    quiz_q = "Which habit most reliably improves sleep quality over time?"
    quiz_opts = ["Taking long daytime naps", "Keeping a consistent wake-up time", "Drinking more coffee in the afternoon", "Heavy late-night workouts"]
    ans = st.radio(quiz_q, quiz_opts, index=None)
    if st.button("Check Answer"):
        if ans is None:
            st.warning("Pick an option first 😊")
        elif ans == "Keeping a consistent wake-up time":
            st.success("Correct! Consistent wake-up anchors the circadian rhythm.")
            st.balloons()
        else:
            st.error("Not quite. Try again!")

with tab3:
    if st.session_state.wellness_plan:
        for msg in st.session_state.chat_history:
            bubble_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
            st.markdown(f'<div class="card {bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        question = st.text_area("Have a question about your plan?", key="chat_input")
        if st.button("Ask Question"):
            if question:
                st.session_state.chat_history.append({"role": "user", "content": question})
                with st.spinner("Thinking..."):
                    prompt = f"Based on this plan:\n{st.session_state.wellness_plan}\n\nUser question: {question}\nAnswer:"
                    answer = generate_ai_response(prompt)
                    st.session_state.chat_history.append({"role": "ai", "content": answer})
                st.experimental_rerun()
    else:
        st.info("Chat will be available after generating a wellness plan.")

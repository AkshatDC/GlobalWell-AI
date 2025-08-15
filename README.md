# GlobalWell AI

**GlobalWell AI** is a personal wellness companion powered by generative AI, designed to help users improve their health, habits, and wellbeing through personalized, actionable guidance—aligned with the United Nations Sustainable Development Goal 3: Good Health and Well-being.

---

## Features

- **Personalized Wellness Plans**  
  Get custom health and lifestyle plans based on your age, gender, location, activity level, diet, and goals.

- **AI-Driven Local Insights**  
  Instantly access hyper-local, seasonal, and affordable nutrition advice, as well as myth-busting wellness facts for your region.

- **Ambient Noise Tools**  
  Play soothing sounds (White Noise, Rain, Brown Noise) to create the optimal focus or relaxation environment.

- **Productivity Aids**  
  Built-in Pomodoro timer and visual breathing orb to support concentration and stress reduction.

- **Gratitude Journal**  
  Mini-journal to log daily gratitude and small wins for better mental health.

- **Health Literacy and Quick Quizzes**  
  Learn and stay motivated with surprises, quizzes, and helpful health facts.

- **Rich Dark Mode UI**  
  Modern, clean design optimized for low-light viewing and focus.

- **Chime for Mindfulness**  
  A custom chime tool to support regular mindful breaks.

---

## Installation

1. **Clone the repository:**
    ```
    git clone https://github.com/AkshatDC/GlobalWell-AI.git
    cd GlobalWell-AI
    ```

2. **Install dependencies (auto-installs on first run):**
    - [Streamlit](https://www.streamlit.io/)
    - [google-generativeai](https://github.com/google/generative-ai-python)
    - [python-dotenv](https://pypi.org/project/python-dotenv/)
    - [reportlab](https://pypi.org/project/reportlab/)

3. **Add your `.env` file:**
    ```
    GEMINI_API_KEY=your_google_generative_ai_key_here
    ```

4. **Place ambient noise files (`.mp3`) in your project directory**  
   Example:  
white-noise-358382.mp3
calming-rain-257596.mp3
soft-brown-noise-299934.mp3

text

5. **Run the app:**
 ```
 streamlit run app.py
 ```

---

## Usage

- Fill your profile details in the sidebar.
- Choose or change your preferred ambient sound and click "Start Noise".
- Set and describe your wellness goal.
- Click `Generate My Wellness Plan` to receive a tailored plan.
- Use productivity, mindfulness, and gratitude tools from the "Local Wellness & Tools" tab—available at all times.
- Download your plan in PDF format for easy reference.
- Use the chime feature or quick health quizzes as additional support.

---

## Screenshots

![GlobalWell AI Demo](./screenshot_demo.png)

---

## File Structure

.
GlobalWell_AI/
├── screenshots/
│   └── screenshot_demo.png
├── .venv/
├── .gitignore
├── .env
├── app.py
└── requirements.txt


---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change or improve.

---

## License

This project is [MIT](LICENSE) licensed.

---

## Credits

- Ambient sound files from [Pixabay Audio](https://pixabay.com/music/)
- Generative AI powered by Google Gemini
- Created by [Akshat Chhatriwala]

---

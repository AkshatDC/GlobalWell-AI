GlobalWell AI 🌍
A personal wellness companion powered by generative AI, designed to help users improve their health, habits, and wellbeing through personalized, actionable guidance—aligned with the United Nations Sustainable Development Goal 3: Good Health and Well-being.

✨ Key Features
Personalized Wellness Plans: Get custom health and lifestyle plans based on your age, gender, location, activity level, diet, and goals.

AI-Driven Local Insights: Instantly access hyper-local, seasonal, and affordable nutrition advice, as well as myth-busting wellness facts for your region.

Ambient Noise Tools: Play soothing sounds (White Noise, Rain, Brown Noise) to create the optimal focus or relaxation environment.

Productivity Aids: Built-in Pomodoro timer and visual breathing orb to support concentration and stress reduction.

Gratitude Journal: A mini-journal to log daily gratitude and small wins for better mental health.

Health Literacy and Quick Quizzes: Learn and stay motivated with surprises, quizzes, and helpful health facts.

Rich Dark Mode UI: Modern, clean design optimized for low-light viewing and focus.

Chime for Mindfulness: A custom chime tool to support regular mindful breaks.

🚀 Installation
Clone the repository:

git clone https://github.com/yourusername/globalwell-ai.git
cd globalwell-ai

Install dependencies (auto-installs on first run):
The application will automatically install the following required packages when you run it for the first time:

Streamlit

google-generativeai

python-dotenv

reportlab

Add your .env file:
Create a file named .env in the root of the project directory and add your Google Gemini API key:

GEMINI_API_KEY=your_google_generative_ai_key_here

Place ambient noise files (.mp3) in your project directory.
The application is designed to look for these specific filenames. Download them and place them in the root folder:

white-noise-358382.mp3

calming-rain-257596.mp3

soft-brown-noise-299934.mp3

Run the app:

streamlit run app.py

🖼️ Features Showcase
Here’s a closer look at some of the key features of GlobalWell AI.

Feature

Screenshot

Description

Personalized Plan

[Placeholder for your screenshot]<br> screenshots/plan_view.png

The app generates a holistic wellness plan, broken down into easy-to-read sections for nutrition, fitness, and mental well-being.

Wellness Tools

[Placeholder for your screenshot]<br> screenshots/tools_view.png

The tools tab includes a breathing orb, a local produce guide, and a wellness myth-buster to enhance health literacy.

Productivity Aids

[Placeholder for your screenshot]<br> screenshots/productivity_view.png

Users can access ambient noise players and a Pomodoro timer to improve focus and create a calming environment.

Gratitude Journal

[Placeholder for your screenshot]<br> screenshots/journal_view.png

A simple and effective tool for logging daily gratitude and small wins to support mental health.

📁 File Structure
GlobalWell_AI/
├── .venv/
├── screenshots/
│   ├── plan_view.png
│   ├── tools_view.png
│   ├── productivity_view.png
│   └── journal_view.png
├── .gitignore
├── .env
├── app.py
├── requirements.txt
├── white-noise-358382.mp3
├── calming-rain-257596.mp3
└── soft-brown-noise-299934.mp3

🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change or improve.

📄 License
This project is licensed under the MIT License.

🙏 Credits
Ambient sound files from Pixabay Audio

Generative AI powered by Google Gemini

Created by [Your Name/Your Team]

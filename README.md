Here is the `README.md` file for **Manifest Me**, tailored to match the style and structure of the example you provided. You can copy and paste this directly into your GitHub repository.

-----

# Manifest Me — AI-Powered Manifestation Guide & Chatbot

**Manifest Me** is a secure, emotionally intelligent web application designed to be a personal companion for manifestation. It helps users set intentions, align their emotions, and receive personalized guidance through a context-aware AI chatbot that remembers their goals and journey.

### 🚀 Features

  * **Secure User System:** Full Sign-up/Login functionality with password hashing (Bcrypt).
  * **Goal-Aligned AI:** The chatbot (Google Gemini) creates responses based on the user's specific saved goals.
  * **Persistent Memory:** All chat history is saved to a cloud database (MongoDB Atlas) so conversations aren't lost.
  * **Weekly Reflection:** An AI-powered tool that analyzes past chat history to summarize emotional patterns and growth.

  * **Emotional Safety:** The AI is prompted to prioritize emotional validation before guiding the user toward their goals.

### 🧰 Tech Stack

  * **Frontend:** HTML5, CSS3, JavaScript
  * **Backend:** Flask (Python)
  * **AI:** Google Gemini API (Generative AI)
  * **Database:** MongoDB Atlas (Cloud)
  * **Authentication:** Flask-Login & Flask-Bcrypt

### 📂 Folder Structure

```text
Manifest-Me/
│── app.py                # Main Flask application & Routes
│── main.py               # Gemini API configuration & Logic
│── requirements.txt      # List of dependencies
│
├── static/               # CSS and Images
│   ├── style.css
│   └── (images)
│
└── templates/            # HTML Pages
    ├── index.html        # Homepage
    ├── login.html        # Login Page
    ├── signup.html       # Signup Page
    ├── goals.html        # Goal Setting Page
    ├── chat.html         # Main Chat Interface
    └── reflection.html   # Weekly Summary Page
```

### ⚙️ Setup Instructions

**1. Clone the repository**

```bash
git clone https://github.com/YourUsername/Manifest-Me.git
cd Manifest-Me
```

**2. Install Dependencies**

```bash
pip install flask flask-pymongo flask-bcrypt flask-login google-generativeai
```

**3. Configure Database & API**

  * Open `app.py` and ensure your MongoDB Connection String is correct.
  * Open `main.py` and ensure your Google Gemini API Key is set.

**4. Run the Server**

```bash
python app.py
```

**5. Open in Browser**
👉 [http://127.0.0.1:5000/](https://www.google.com/search?q=http://127.0.0.1:5000/)

### 📌 Project Summary

Manifest Me blends modern web security with advanced AI to create a safe space for personal growth. Unlike generic chatbots, it uses a persistent database to "remember" the user, allowing for deep, context-aware conversations about their specific life goals and emotional state.

### 🔮 Future Enhancements

  * Mobile App version (React Native)
  * Voice-to-Text input for hands-free journaling
  * Community feature for sharing success stories
  * Dark Mode toggle
  * Gamified streaks for daily manifesting


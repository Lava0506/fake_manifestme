from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId 
from main import generate
from datetime import datetime

app = Flask(__name__)




app.config["SECRET_KEY"] = "blahblah" 



app.config["MONGO_URI"] = "mongodb+srv://lavanyaluhan:lava@manifestme.ulaay5u.mongodb.net/manifest_me_db?appName=manifestme"



mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page' # Tells flask-login where to send users if they try to access a protected page
login_manager.login_message_category = 'info'


users_collection = mongo.db.users 




class User(UserMixin):
    def __init__(self, user_doc): 
        self.id = str(user_doc["_id"])
        self.email = user_doc["email"]
       

@login_manager.user_loader
def load_user(user_id):
    # This function is used by flask-login to find a user in our database
    user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_doc:
        return User(user_doc)
    return None




@app.route("/signup", methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
       
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists in our 'users_collection'
        existing_user = users_collection.find_one({'email': email})

        if existing_user:
            flash('That email already exists. Please log in.', 'danger')
            return redirect(url_for('login_page'))

        # If user is new, hash their password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert the new user into the 'users_collection'
        users_collection.insert_one({'email': email, 'password': hashed_password})
        
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login_page'))

    # If it's a GET request, just show the signup page
    return render_template('signup.html')


@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find the user in our 'users_collection'
        user_doc = users_collection.find_one({'email': email})

        # Check if the user exists AND the password is correct
        if user_doc and bcrypt.check_password_hash(user_doc['password'], password):
            
            # Create the User object (from the User class we made)
            user_obj = User(user_doc)
            
            # Log them in with flask-login
            login_user(user_obj)
            
            # Send them to the homepage
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')

    # If it's a GET request or login failed, show the login page
    return render_template('login.html')


@app.route("/logout")
@login_required  # This ensures only logged-in users can access this
def logout():
    logout_user()
    return redirect(url_for('home'))
# 1:Home Page
# When a user visits the main URL, this shows them the chat page.
@app.route("/")
def home():
    if current_user.is_authenticated:
        # 1. Check MongoDB to see if this user has saved goals
        user_data = mongo.db.goals.find_one({"user_id": current_user.id})
        
        if user_data and user_data.get("goals"):
            # User HAS goals -> Send straight to Chat
            return redirect(url_for('chat_page'))
        else:
            # User has NO goals -> Send to Goals Page
            return redirect(url_for('goals_page'))
            
    # Not logged in -> Show the landing page
    return render_template("index.html")


@app.route("/goals")
@login_required  # <-- ADD THIS LINE
def goals_page():
    return render_template("goals.html")
# Route 2: The Chat Logic
# This route ONLY listens for POST requests fromJavaScript.
# It receives the user's message and returns the bot's reply.
@app.route("/chat", methods=['GET', 'POST'])
@login_required
def chat_page():
    if request.method == 'POST':
        user_msg = request.json["message"]
        
        # 1. Retrieve the user's goals from MongoDB
        user_data = mongo.db.goals.find_one({"user_id": current_user.id})
        if user_data and user_data.get("goals"):
            goals_text = ", ".join(user_data["goals"])
        else:
            goals_text = "General happiness and well-being" # Default if no goals found

        # 2. Create the "System Prompt" (The Secret Instructions)
        # This tells Gemini to act as a guide and use the goals
        system_prompt = f"""
        You are 'Manifest Me', an emotionally intelligent manifestation companion.
        The user's saved long-term goals are: {goals_text}.
        
        User's Message: "{user_msg}"
        
        YOUR BEHAVIOR GUIDELINES:
        
        1. 🛡️ EMOTIONAL SAFETY FIRST: 
           - If the user seems low, sad, or anxious, prioritize comforting them. Do NOT force a goal on them immediately. Help them feel better first.
           
        2. 🤝 THE "ALIGNMENT" QUESTION:
           - If the user shares a journal entry or emotion, do not assume which goal it fits.
           - Instead, validate the feeling, then SOFTLY ask: "Would you like to align this feeling with one of your goals ({goals_text}) today, or focus on something else?"
           
        3. ✨ THE MANIFESTATION SESSION (Only generate this if the user asks or selects a goal):
           - If the user explicitly wants to focus on a goal, provide exactly this structure:
             * 🗣️ **Personalized Affirmation**
             * 👁️ **Visualization Script** (Write a vivid 3-4 sentence script suitable for text-to-speech)
             * 💌 **Motivational Message**
             * 👣 **Small Action Step** (A tiny, easy step they can take today)
        
        Keep your tone warm, magical, and non-judgmental.
        """

        # 3. Send to Gemini
        bot_reply = generate(system_prompt)  
        # 4. Save this interaction to MongoDB
        # We save WHO said it, WHAT they said, and WHEN they said it.
        mongo.db.sessions.insert_one({
            "user_id": current_user.id,
            "user_message": user_msg,
            "bot_reply": bot_reply,
            "timestamp": datetime.utcnow() # This is crucial for Weekly Reflection!
        })    
        return jsonify({"reply": bot_reply}) 
    
    return render_template("chat.html")
# --- WEEKLY REFLECTION ROUTE ---
@app.route("/reflection")
@login_required
def reflection_page():
    # 1. Find all sessions for this user
    # (In a real app, we'd filter by date, but for the Viva, getting ALL is fine!)
    user_sessions = list(mongo.db.sessions.find({"user_id": current_user.id}))

    if not user_sessions:
        summary = "You haven't started your journey yet! Chat with the guide to generate insights."
    else:
        # 2. Prepare the data for Gemini
        # We combine all previous user messages into one big text block
        history_text = ""
        for session in user_sessions:
            history_text += f"- {session.get('user_message', '')}\n"

        # 3. Ask Gemini to summarize
        reflection_prompt = f"""
        Here are the journal entries/chat messages from a user this week:
        
        {history_text}
        
        Please act as a Manifestation Coach. 
        1. Identify the common emotional themes (e.g., "You focused a lot on...")
        2. Offer 2 specific tips for the next week based on these patterns.
        3. Keep it warm, encouraging, and under 150 words.
        """
        
        summary = generate(reflection_prompt)

    # 4. Show the page
    # We use .replace to make newlines look good in HTML
    return render_template("reflection.html", summary_text=summary.replace("\n", "<br>"))
# This line runs the app. It must be at the very end.
# --- SAVE GOALS ROUTE ---
@app.route("/save-goals", methods=["POST"])
@login_required
def save_goals():
    # 1. Get the data from JavaScript
    data = request.json
    goals_list = data.get("goals")

    print(f"DEBUG: Saving goals for User {current_user.id}: {goals_list}") # Debug print

    # 2. Save to MongoDB
    # We use 'update_one' with 'upsert=True'
    # This means: "If goals exist, update them. If not, create new ones."
    mongo.db.goals.update_one(
        {"user_id": current_user.id}, 
        {"$set": {"goals": goals_list}}, 
        upsert=True
    )

    return jsonify({"success": True})
if __name__ == "__main__":
    app.run(debug=True) 


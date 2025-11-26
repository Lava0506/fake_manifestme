import os
import google.generativeai as genai
from dotenv import load_dotenv

# Configur
load_dotenv() 
API_KEY = os.getenv("GEN_AI_KEY") 
genai.configure(api_key=API_KEY) 

# Model Selection 
model = genai.GenerativeModel('gemini-2.5-flash')

# Generation Function 
# This part gets imported by app.py
def generate(prompt):
    response = model.generate_content(prompt) 
    return response.text 

# --- Test Section ---
# This part is IGNORED by app.py.
# It ONLY runs when you type `python main.py` in the terminal.
if __name__ == "__main__":
    print("--- Running a direct test of main.py ---")
    test_response = generate("Tell me a fun fact about the Roman Empire.")
    print(test_response)
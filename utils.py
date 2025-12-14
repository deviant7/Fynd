import google.genai as genai
import json
import pandas as pd
import os
import datetime

# --- CONFIGURATION ---
# In production (Streamlit Cloud), these will come from st.secrets
# locally, you can set them here or use environment variables
API_KEY = "AIzaSyBwwe-oCG98nwb6dCNo_oCRIKlcwi7zV60" 
DB_FILE = "reviews_data.csv"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

def get_ai_analysis(rating, review_text):
    """
    Generates User Reply, Admin Summary, and Action Items in ONE call.
    """
    prompt = f"""
    You are an AI customer service manager.
    A customer just left this review:
    Rating: {rating}/5 Stars
    Review: "{review_text}"

    Task:
    1. Write a polite, empathetic response to the user.
    2. Summarize the review in 5-10 words for the admin.
    3. Suggest one concrete 'Recommended Action' for the business to fix or improve this.

    Output strictly in JSON:
    {{
        "user_response": "...",
        "admin_summary": "...",
        "recommended_action": "..."
    }}
    """
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return {
            "user_response": "Thank you for your feedback!",
            "admin_summary": "Error generating summary.",
            "recommended_action": "Check system logs."
        }

def load_data():
    """Loads data from the shared CSV/Database"""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["timestamp", "rating", "review", "user_response", "summary", "action"])

def save_data(rating, review, ai_data):
    """Saves new submission to the shared CSV/Database"""
    df = load_data()
    
    new_row = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rating": rating,
        "review": review,
        "user_response": ai_data['user_response'],
        "summary": ai_data['admin_summary'],
        "action": ai_data['recommended_action']
    }
    
    # In a real app with Google Sheets, you would append to the sheet here
    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    updated_df.to_csv(DB_FILE, index=False)
    return True
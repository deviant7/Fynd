import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- CONFIGURATION ---
# These should be set in Streamlit Secrets for deployment
# API_KEY = st.secrets["GOOGLE_API_KEY"] 

def get_ai_analysis(rating, review_text):
    """
    Calls Gemini to generate User Reply, Summary, and Action.
    """
    # Configure API (Ensure you set this in your main app or secrets)
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except:
        return {"user_response": "System Error: API Key missing.", "admin_summary": "Error", "recommended_action": "Check Config"}

    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    Analyze this customer review:
    Rating: {rating}/5
    Review: "{review_text}"

    Return JSON:
    {{
        "user_response": "Polite reply to customer.",
        "admin_summary": "5-word summary for internal use.",
        "recommended_action": "1 concrete action step."
    }}
    """
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception:
        return {
            "user_response": "Thank you for your feedback!",
            "admin_summary": "Auto-generation failed.",
            "recommended_action": "Review manually."
        }

def load_data():
    """Loads data from the shared Google Sheet"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 ensures we don't cache old data, keeping the admin view live
    return conn.read(worksheet="Sheet1", ttl=0)

def save_data(rating, review, ai_data):
    """Appends new review to the shared Google Sheet"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    existing_data = conn.read(worksheet="Sheet1", ttl=0)
    
    new_entry = pd.DataFrame([{
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rating": rating,
        "review": review,
        "user_response": ai_data['user_response'],
        "summary": ai_data['admin_summary'],
        "action": ai_data['recommended_action']
    }])
    
    updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
    conn.update(worksheet="Sheet1", data=updated_df)
    return True
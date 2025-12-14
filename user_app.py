import streamlit as st
import utils

st.set_page_config(page_title="Feedback Portal", page_icon="⭐")

st.title("🗣️ Share Your Experience")
st.write("We use AI to read every review immediately.")

with st.form("feedback_form"):
    rating = st.slider("Rate us:", 1, 5, 5)
    review_text = st.text_area("What did you think?")
    submit_btn = st.form_submit_button("Submit")

if submit_btn and review_text:
    with st.spinner("Processing your feedback..."):
        # 1. AI Processing
        ai_result = utils.get_ai_analysis(rating, review_text)
        
        # 2. Save to Shared Google Sheet
        try:
            utils.save_data(rating, review_text, ai_result)
            st.success("Sent! Thank you.")
            
            # 3. AI Reply
            st.info(f"💬 **Our Reply:** {ai_result['user_response']}")
        except Exception as e:
            st.error(f"Database Error: {e}")
            
elif submit_btn:
    st.warning("Please enter some text.")
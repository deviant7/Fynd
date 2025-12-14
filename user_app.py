import streamlit as st
import utils

st.set_page_config(page_title="Feedback Portal", page_icon="⭐")

st.title("🗣️ Share Your Experience")
st.write("We use AI to read every review immediately.")

# ----------------------------
# Session state initialization
# ----------------------------
if "review_input" not in st.session_state:
    st.session_state["review_input"] = ""

def clear_text():
    st.session_state["review_input"] = ""

# ----------------------------
# Feedback Form
# ----------------------------
with st.form("feedback_form"):
    rating = st.slider("Rate us:", 1, 5, 5)
    review_text = st.text_area(
        "What did you think?",
        key="review_input"
    )
    submit_btn = st.form_submit_button("Submit")

# ----------------------------
# Form submission logic
# ----------------------------
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

            # Reset option for next user
            st.button("Submit Another Review", on_click=clear_text)

        except Exception as e:
            st.error(f"Database Error: {e}")

elif submit_btn:
    st.warning("Please enter some text.")

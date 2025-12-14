import streamlit as st
import plotly.express as px
import utils

st.set_page_config(page_title="Admin Console", page_icon="🔒", layout="wide")
st.title("🔒 Live Feedback Monitor")

if st.button("Refresh Data"):
    st.rerun()

# Load from the same Shared Google Sheet
try:
    df = utils.load_data()
except Exception:
    st.error("Could not load data. Check database connection.")
    st.stop()

if not df.empty:
    # Top Stats
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Reviews", len(df))
    c2.metric("Avg Rating", f"{df['rating'].mean():.1f} ⭐")
    c3.metric("Latest Sentiment", df['summary'].iloc[-1] if len(df) > 0 else "N/A")

    st.divider()

    # Visuals
    col_chart, col_actions = st.columns([1, 1])
    with col_chart:
        st.subheader("Ratings Trend")
        fig = px.histogram(df, x="rating", nbins=5, title="Score Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col_actions:
        st.subheader("⚠️ Recommended Actions")
        # Show actions for reviews with 3 stars or less
        issues = df[df['rating'] <= 3]
        if not issues.empty:
            for _, row in issues.tail(3).iterrows():
                st.warning(f"**Issue:** {row['summary']}\n\n**Fix:** {row['action']}")
        else:
            st.success("No urgent issues found.")

    st.divider()
    st.subheader("Raw Data Feed")
    st.dataframe(df.sort_values(by="timestamp", ascending=False), use_container_width=True)

else:
    st.info("Waiting for first review...")
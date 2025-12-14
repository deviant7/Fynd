import streamlit as st
import plotly.express as px
import pandas as pd
import utils

# Page Configuration
st.set_page_config(page_title="Admin Console", page_icon="🔒", layout="wide")
st.title("🔒 Live Feedback Monitor")

# Sidebar for manual refresh
if st.sidebar.button("Refresh Data"):
    st.rerun()

# --- 1. Load Data ---
try:
    df = utils.load_data()
except Exception as e:
    st.error(f"Could not load data. Check database connection. Error: {e}")
    st.stop()

if not df.empty:
    # Ensure proper data types
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # --- 2. Top Level Metrics ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Reviews", len(df))
    
    avg_rating = df['rating'].mean()
    c2.metric("Avg Rating", f"{avg_rating:.1f} ⭐")
    
    # Get the latest summary (if available)
    latest_summary = df['summary'].iloc[-1] if 'summary' in df.columns and len(df) > 0 else "N/A"
    c3.metric("Latest Sentiment", str(latest_summary)[:30] + "...")

    st.divider()

    # --- 3. Visual Analytics ---
    col_chart_left, col_chart_right = st.columns(2)

    with col_chart_left:
        # A. Score Distribution (Histogram)
        st.subheader("Score Distribution")
        fig_hist = px.histogram(df, x="rating", nbins=5, title="Count by Stars", color_discrete_sequence=['#636EFA'])
        fig_hist.update_layout(bargap=0.2)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_chart_right:
        # B. Ratings Trend Over Time (Line Chart) - IMPROVEMENT 1
        st.subheader("Ratings Trend")
        # Group by date to see daily average
        df['date'] = df['timestamp'].dt.date
        daily_avg = df.groupby('date')['rating'].mean().reset_index()
        
        if not daily_avg.empty:
            fig_trend = px.line(daily_avg, x='date', y='rating', markers=True, title="Daily Average Rating")
            fig_trend.update_yaxes(range=[0.5, 5.5])  # Fix y-axis to 1-5 scale
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Not enough data for trend analysis.")

    st.divider()

    # --- 4. Actionable Insights with "Done" Checkbox - IMPROVEMENT 2 ---
    st.subheader("⚠️ Recommended Actions")
    
    # Filter for low ratings (3 stars or less)
    issues = df[df['rating'] <= 3].copy()
    
    if not issues.empty:
        # Initialize session state to track "Done" items if not present
        if "done_actions" not in st.session_state:
            st.session_state["done_actions"] = []

        # Display active issues
        count_shown = 0
        for index, row in issues.sort_values(by="timestamp", ascending=False).iterrows():
            # Create a unique key for each row to track state
            unique_key = f"{row['timestamp']}_{index}"
            
            # Only show if not marked as done in this session
            if unique_key not in st.session_state["done_actions"]:
                with st.container():
                    col_msg, col_btn = st.columns([4, 1])
                    with col_msg:
                        st.warning(f"**Issue:** {row['summary']}\n\n**Fix:** {row['action']}")
                    with col_btn:
                        # The "Done" Button
                        if st.button("✅ Done", key=f"btn_{unique_key}"):
                            st.session_state["done_actions"].append(unique_key)
                            st.rerun() # Rerun to hide the item immediately
                count_shown += 1
        
        if count_shown == 0:
            st.success("🎉 All urgent issues marked as resolved for this session!")
    else:
        st.success("No urgent issues found (Ratings > 3).")

    st.divider()

    # --- 5. Raw Data Feed with Download - IMPROVEMENT 3 ---
    col_header, col_download = st.columns([4, 1])
    with col_header:
        st.subheader("Raw Data Feed")
    with col_download:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name='customer_feedback.csv',
            mime='text/csv',
        )

    # Display the full table
    st.dataframe(
        df[['timestamp', 'rating', 'review', 'user_response', 'summary', 'action']].sort_values(by="timestamp", ascending=False), 
        use_container_width=True
    )

else:
    st.info("Waiting for first review...")
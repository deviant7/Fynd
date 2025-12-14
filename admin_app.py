import streamlit as st
import plotly.express as px
import pandas as pd
import utils
from streamlit_gsheets import GSheetsConnection

# Page Configuration
st.set_page_config(page_title="Admin Console", page_icon="🔒", layout="wide")
st.title("🔒 Live Feedback Monitor")

# --- 1. Top Refresh Button (Restored Position) ---
if st.button("Refresh Data"):
    st.rerun()

# --- 2. Load Data ---
try:
    # We use the connection directly here to allow writing updates back to the sheet
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Sheet1", ttl=0)
except Exception as e:
    st.error(f"Could not load data. Check database connection. Error: {e}")
    st.stop()

if not df.empty:
    # Ensure proper data types
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Fill NaN values to avoid errors
    df['action'] = df['action'].fillna("")

    # --- 3. Top Level Metrics ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Reviews", len(df))
    
    avg_rating = df['rating'].mean()
    c2.metric("Avg Rating", f"{avg_rating:.1f} ⭐")
    
    latest_summary = df['summary'].iloc[-1] if 'summary' in df.columns and len(df) > 0 else "N/A"
    c3.metric("Latest Sentiment", str(latest_summary)[:30] + "...")

    st.divider()

    # --- 4. Visual Analytics ---
    col_chart_left, col_chart_right = st.columns(2)

    with col_chart_left:
        st.subheader("Score Distribution")
        fig_hist = px.histogram(df, x="rating", nbins=5, title="Count by Stars", color_discrete_sequence=['#636EFA'])
        fig_hist.update_layout(bargap=0.2)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_chart_right:
        st.subheader("Ratings Trend")
        df['date'] = df['timestamp'].dt.date
        daily_avg = df.groupby('date')['rating'].mean().reset_index()
        
        if not daily_avg.empty:
            fig_trend = px.line(daily_avg, x='date', y='rating', markers=True, title="Daily Average Rating")
            fig_trend.update_yaxes(range=[0.5, 5.5])
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Not enough data for trend analysis.")

    st.divider()

    # --- 5. Actionable Insights (With Persistence) ---
    st.subheader("⚠️ Recommended Actions")
    
    # Filter: Low rating AND not already resolved
    # We check if "(RESOLVED)" is already in the action text
    issues = df[(df['rating'] <= 3) & (~df['action'].str.contains(r"\(RESOLVED\)", na=False))].copy()
    
    if not issues.empty:
        count_shown = 0
        # Sort by latest first
        for index, row in issues.sort_values(by="timestamp", ascending=False).iterrows():
            with st.container():
                col_msg, col_btn = st.columns([4, 1])
                with col_msg:
                    st.warning(f"**Issue:** {row['summary']}\n\n**Fix:** {row['action']}")
                with col_btn:
                    # Unique key for each button
                    if st.button("✅ Done", key=f"btn_{index}"):
                        # 1. Update the local dataframe
                        # We append (RESOLVED) to the action text so it gets filtered out next time
                        current_action = df.at[index, 'action']
                        df.at[index, 'action'] = f"{current_action} (RESOLVED)"
                        
                        # 2. Write the UPDATED dataframe back to Google Sheets
                        # This makes the "Done" status persistent across refreshes
                        conn.update(worksheet="Sheet1", data=df)
                        
                        # 3. Rerun to refresh the UI immediately
                        st.rerun()
            count_shown += 1
    else:
        st.success("No urgent issues found (or all marked resolved).")

    st.divider()

    # --- 6. Raw Data Feed with Download ---
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

    st.dataframe(
        df[['timestamp', 'rating', 'review', 'user_response', 'summary', 'action']].sort_values(by="timestamp", ascending=False), 
        use_container_width=True
    )

else:
    st.info("Waiting for first review...")
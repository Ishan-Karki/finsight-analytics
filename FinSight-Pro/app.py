import streamlit as st
import pandas as pd
import numpy as np
import processor
from ui.sidebar import render_sidebar
from ui.dashboard import render_dashboard
from ui.chatbot import render_chatbot

# Configure the page setting
st.set_page_config(
    page_title="FinSight-Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for transactions (In-memory only)
if "session_transactions" not in st.session_state:
    st.session_state.session_transactions = pd.DataFrame()

# ----------------- SIDEBAR -----------------
uploaded_file = render_sidebar()

# ----------------- MAIN CONTENT -----------------
tab1, tab2 = st.tabs(["📊 Current Analysis", "🤖 AI Assistant"])

with tab1:
    if uploaded_file is not None:
        st.success(f"Processing `{uploaded_file.name}`...")
        with st.spinner('Analyzing with Gemini AI...'):
            df, category_totals, daily_trend = processor.process_with_ai(uploaded_file)
        
        if df is not None:
            # Append to session state for the chatbot to know about it
            st.session_state.session_transactions = pd.concat([st.session_state.session_transactions, df]).drop_duplicates().reset_index(drop=True)
            st.success("Analysis complete! Chatbot is now aware of these transactions.")
            render_dashboard(df, category_totals, daily_trend)
    else:
        render_dashboard(None, None, None)

with tab2:
    render_chatbot()

# ----------------- FOOTER -----------------
footer_css = """
<style>
.footer { 
    position: fixed; 
    left: 0; 
    bottom: 0; 
    width: 100%; 
    background-color: transparent; 
    color: #a0a0a0; 
    text-align: center; 
    padding: 10px; 
    font-size: 0.8rem; 
    border-top: 1px solid #333; 
    z-index: 100; 
}
.block-container { padding-bottom: 80px; }
</style>
<div class="footer">
    🔒 <strong>Privacy First:</strong> Data is stored in-memory and cleared after the session ends. Analysis powered by Gemini AI.
</div>
"""
st.markdown(footer_css, unsafe_allow_html=True)

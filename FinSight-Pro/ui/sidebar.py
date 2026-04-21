import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.header("📂 Data Upload")
        st.write("Upload your bank statement to start analyzing.")
        
        # Accept multiple file types
        uploaded_file = st.file_uploader(
            "Choose a file (CSV, TXT, PDF, Image)", 
            type=["csv", "txt", "pdf", "jpg", "jpeg", "png"]
        )
        
        st.markdown("---")
        st.markdown(
            """
            ### About FinSight-Pro
            FinSight-Pro provides advanced analytics and insights into your personal finances securely.
            Now powered by Gemini AI for smart data extraction and conversational analysis!
            """
        )
        return uploaded_file

import streamlit as st
import processor

# Configure the page setting to Wide Mode
st.set_page_config(
    page_title="FinSight-Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.header("📂 Data Upload")
    st.write("Upload your bank statement to start analyzing.")
    # Accept only .csv files
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    st.markdown("---")
    st.markdown(
        """
        ### About FinSight-Pro
        FinSight-Pro provides advanced analytics and insights into your personal finances securely.
        """
    )

# ----------------- MAIN CONTENT -----------------
if uploaded_file is None:
    # High-quality Welcome Dashboard
    st.title("Welcome to FinSight-Pro 📊")
    st.markdown("### Please upload a bank CSV to begin your local-only analysis.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Placeholder metrics layout for high-quality feel
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Balance", value="$ --.--")
    with col2:
        st.metric(label="Income", value="$ --.--")
    with col3:
        st.metric(label="Expenses", value="$ --.--")
    with col4:
        st.metric(label="Savings Rate", value="-- %")
        
    st.markdown("---")
    
    st.info("✨ **Tip:** Your data is processed entirely in your browser/local machine. We do not store or transmit any of your financial data.", icon="ℹ️")

else:
    # This block will run once the user uploads a CSV
    st.success(f"Successfully uploaded `{uploaded_file.name}`! Preparing analysis dashboard...")
    
    df, category_totals, daily_trend = processor.process_bank_data(uploaded_file)
    
    if df is not None:
        st.markdown("---")
        st.header("📊 Financial Overview")
        
        # Display Top Level Metrics
        total_spent = category_totals['Amount'].sum()
        total_transactions = len(df)
        
        m1, m2 = st.columns(2)
        m1.metric("Total Tracked Volume", f"${total_spent:,.2f}")
        m2.metric("Total Transactions", f"{total_transactions}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📈 Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Total by Category**")
            st.dataframe(category_totals, use_container_width=True, hide_index=True)
            
        with col2:
            st.write("**Daily Spending Trend**")
            st.line_chart(daily_trend, x="Date", y="Amount")
            
        st.markdown("### 🔍 Transaction Log")
        st.dataframe(df, use_container_width=True)

# ----------------- FOOTER -----------------
# Inject custom CSS to construct a fixed footer with the privacy disclaimer
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
    font-size: 0.9rem;
    border-top: 1px solid #333;
    z-index: 100;
}
/* Ensure the main content doesn't get hidden behind the footer */
.block-container {
    padding-bottom: 60px;
}
</style>
<div class="footer">
    🔒 <strong>Privacy Disclaimer:</strong> Data remains on your local machine. No external databases are used.
</div>
"""
st.markdown(footer_css, unsafe_allow_html=True)

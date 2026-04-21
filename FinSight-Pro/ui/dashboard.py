import streamlit as st
import plotly.express as px
import pandas as pd

def _calculate_running_balance(df: pd.DataFrame) -> pd.Series:
    """Return per-transaction post-transaction balance with AI-provided balance as anchor when present."""
    net_amount = df.apply(
        lambda x: x['Amount'] if x['Category'] == 'Deposit' else -x['Amount'],
        axis=1
    ).astype(float)
    cumulative_net = net_amount.cumsum()

    provided_balance = pd.to_numeric(df.get('Balance', pd.Series(index=df.index, dtype=float)), errors='coerce')
    anchor_index = provided_balance.first_valid_index()

    if anchor_index is not None:
        start_balance = float(provided_balance.loc[anchor_index] - cumulative_net.loc[anchor_index])
    else:
        start_balance = 0.0

    computed_balance = start_balance + cumulative_net
    final_balance = provided_balance.fillna(computed_balance).round(2)
    return final_balance

def render_dashboard(df, category_totals, daily_trend):
    if df is not None:
        df = df.copy()
        # Dashboard Metrics
        deposits = df[df['Category'] == 'Deposit']['Amount'].sum()
        withdrawals = df[df['Category'] == 'Withdraw']['Amount'].sum()
        net_balance = deposits - withdrawals
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Deposits", f"Rs. {deposits:,.2f}")
        m2.metric("Total Withdrawals", f"Rs. {withdrawals:,.2f}", delta=f"Net: Rs. {net_balance:,.2f}")
        m3.metric("Transaction Count", f"{len(df)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Expenses by Category**")
            fig_donut = px.pie(
                category_totals, 
                values='Amount', 
                names='Category', 
                hole=0.4,
                color='Category',
                color_discrete_map={'Deposit': '#4CAF50', 'Withdraw': '#E53935'} # Green for Deposit, Red for Withdraw
            )
            fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_donut, use_container_width=True)
            
        with col2:
            st.write("**Net Balance Trend**")
            # Calculate daily net flow
            df['Net_Amount'] = df.apply(lambda x: x['Amount'] if x['Category'] == 'Deposit' else -x['Amount'], axis=1)
            daily_net = df.groupby(df['Date'].dt.date)['Net_Amount'].sum().reset_index()
            daily_net.columns = ['Date', 'Net_Flow']
            daily_net['Cumulative_Balance'] = daily_net['Net_Flow'].cumsum()
            
            fig_line = px.line(
                daily_net, 
                x='Date', 
                y='Cumulative_Balance',
                markers=True,
                line_shape='hv' # Step chart looks better for balance
            )
            fig_line.update_layout(
                yaxis_title="Balance (Rs.)",
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
        st.markdown("### 🔍 Current Transaction Log")
        
        # Calculate running balance per transaction
        df = df.sort_values(by='Date').reset_index(drop=True)
        if 'Net_Amount' not in df.columns:
            df['Net_Amount'] = df.apply(lambda x: x['Amount'] if x['Category'] == 'Deposit' else -x['Amount'], axis=1)

        df['Balance'] = _calculate_running_balance(df)
        
        # Display the dataframe with the new Balance column, hiding Net_Amount to replace it
        display_df = df.drop(columns=['Net_Amount']) if 'Net_Amount' in df.columns else df
        st.dataframe(display_df, use_container_width=True)
    else:
        # Default Welcome State
        st.title("Welcome to FinSight-Pro 📊")
        st.markdown("### Please upload a financial document to begin.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric(label="Total Balance", value="Rs. --.--")
        with col2: st.metric(label="Income", value="Rs. --.--")
        with col3: st.metric(label="Expenses", value="Rs. --.--")
        with col4: st.metric(label="Savings Rate", value="-- %")
            
        st.markdown("---")
        st.info("✨ **Tip:** Your data is processed smartly using AI. Supported formats include CSV, PDF, TXT, and Images.", icon="ℹ️")

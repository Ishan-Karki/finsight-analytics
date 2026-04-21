import streamlit as st
import plotly.express as px
import database

def render_history():
    st.header("📜 Lifetime Transaction History")
    history_df = database.get_all_transactions()
    
    if not history_df.empty:
        st.write(f"Total historical records: {len(history_df)}")
        
        # Summary Metrics for History
        h_col1, h_col2, h_col3 = st.columns(3)
        total_hist_spend = history_df['amount'].sum()
        avg_trans = history_df['amount'].mean()
        
        h_col1.metric("Total Lifetime Spend", f"Rs. {total_hist_spend:,.2f}")
        h_col2.metric("Average Transaction", f"Rs. {avg_trans:,.2f}")
        h_col3.metric("Data Points", len(history_df))
        
        st.dataframe(history_df, use_container_width=True)
        
        # All time category chart
        all_cat_totals = history_df.groupby('category')['amount'].sum().reset_index()
        fig_hist = px.bar(
            all_cat_totals, 
            x='category', 
            y='amount', 
            title="Spending Distribution (All Time)", 
            color='category',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_hist.update_layout(yaxis_title="Amount (Rs.)", xaxis_title="Category")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No historical data found. Upload a file to see your lifetime analytics.")

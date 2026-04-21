import pandas as pd
import streamlit as st

def load_and_process_csv(uploaded_file):
    \"\"\"
    Loads the uploaded CSV, performs fuzzy column matching, 
    converts dates, and validates data.
    \"\"\"
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read the file. Error: {e}")
        return None

    # Expected column mapping with possible aliases for fuzzy matching
    expected_mapping = {
        'Date': ['date', 'transaction date', 'posting date', 'timestamp'],
        'Description': ['description', 'desc', 'memo', 'payee', 'transaction', 'details'],
        'Amount': ['amount', 'cost', 'value', 'transaction amount', 'price', 'spending'],
        'Category': ['category', 'type', 'group', 'classification']
    }

    # Normalize existing columns to lowercase for easier matching
    original_cols = df.columns.tolist()
    normalized_cols = {col.strip().lower(): col for col in original_cols}

    rename_dict = {}
    missing_cols = []

    # Attempt to fuzzy match columns
    for expected_col, aliases in expected_mapping.items():
        found = False
        for original_lower, original_raw in normalized_cols.items():
            if any(alias in original_lower or original_lower in alias for alias in aliases):
                rename_dict[original_raw] = expected_col
                found = True
                break
        
        if not found:
            missing_cols.append(expected_col)

    if missing_cols:
        st.error(f"""
        **Missing Required Columns!**  
        We couldn't automatically map your columns to the following required fields:  
        `{', '.join(missing_cols)}`

        Your columns were: `{', '.join(original_cols)}`

        Please ensure your CSV has columns that clearly indicate the Date, Description, Amount, and Category.
        """)
        return None

    # Rename matched columns
    df = df.rename(columns=rename_dict)

    # Convert Date column to datetime
    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Drop rows where the Date is invalid
        df = df.dropna(subset=['Date'])
    except Exception as e:
        st.error("Failed to parse the 'Date' column. Please ensure dates are formatted properly.")
        return None
        
    # Ensure Amount is numeric
    if df['Amount'].dtype == 'object':
        df['Amount'] = df['Amount'].astype(str).str.replace(r'[\$,]', '', regex=True)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    # Fill missing values for Display
    df['Description'] = df['Description'].fillna("Unknown")
    df['Category'] = df['Category'].fillna("Uncategorized")
    
    return df

def get_category_aggregates(df):
    \"\"\"
    Groups data by Category to calculate total spend.
    \"\"\"
    if df is None or df.empty:
        return pd.DataFrame()
    return df.groupby('Category', as_index=False)['Amount'].sum().sort_values(by='Amount', ascending=True)

def get_daily_trend(df):
    \"\"\"
    Groups data by Date for a daily spend trend.
    \"\"\"
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Extract just the date part for grouping
    trend_df = df.groupby(df['Date'].dt.date)['Amount'].sum().reset_index()
    # Ensure the date column is explicitly named Date
    trend_df = trend_df.rename(columns={'index': 'Date'})
    trend_df = trend_df.sort_values(by='Date')
    return trend_df

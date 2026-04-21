import pandas as pd
import streamlit as st

def process_bank_data(uploaded_file):
    """
    Loads uploaded CSV into a DataFrame, performs fuzzy column matching, 
    converts dates, and calculates category & daily groupings.
    
    Returns:
        tuple: (cleaned_dataframe, category_grouped_dataframe, daily_trend_dataframe)
    """
    # 1. Load CSV
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read the file. Error: {e}")
        return None, None, None

    # 2. Fuzzy Column Mapping
    expected_mapping = {
        'Date': ['date', 'transaction date', 'posting date', 'timestamp'],
        'Description': ['description', 'desc', 'memo', 'payee', 'transaction', 'details'],
        'Amount': ['amount', 'cost', 'value', 'transaction amount', 'price', 'spending'],
        'Category': ['category', 'type', 'group', 'classification']
    }

    normalized_cols = {col.strip().lower(): col for col in df.columns}
    rename_dict = {}
    missing_cols = []

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
        st.error(f"Please rename your columns! Missing required columns loosely resembling: {', '.join(missing_cols)}. "
                 f"Found columns: {', '.join(df.columns.tolist())}")
        return None, None, None

    df = df.rename(columns=rename_dict)

    # 3. Proper Datetime Conversion
    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
    except Exception as e:
        st.error("Failed to parse 'Date' column format.")
        return None, None, None
        
    # Standardize numeric values
    if df['Amount'].dtype == 'object':
        df['Amount'] = df['Amount'].astype(str).str.replace(r'[\$,]', '', regex=True)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    df['Description'] = df['Description'].fillna("Unknown")
    df['Category'] = df['Category'].fillna("Uncategorized")
    
    # 4. Group data by Category and Date
    category_totals = df.groupby('Category', as_index=False)['Amount'].sum().sort_values(by='Amount')
    
    # Group by date for daily trend
    daily_trend = df.groupby(df['Date'].dt.date)['Amount'].sum().reset_index()
    daily_trend.rename(columns={'index': 'Date' if 'index' in daily_trend.columns else 'Date'}, inplace=True)
    daily_trend = daily_trend.sort_values(by='Date')
    
    return df, category_totals, daily_trend

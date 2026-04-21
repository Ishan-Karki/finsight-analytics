import pandas as pd
import streamlit as st

def process_bank_data(uploaded_file):
    """
    Loads uploaded CSV into a DataFrame, performs fuzzy column matching, 
    converts dates, and calculates category & daily groupings.
    
    Returns:
        tuple: (cleaned_dataframe, category_grouped_dataframe, daily_trend_dataframe)
    """
    # 1. Load CSV with auto header detection
    try:
        sample_df = pd.read_csv(uploaded_file, header=None, nrows=30)
        
        expected_mapping = {
            'Date': ['date', 'time', 'posting', 'txn', 'transaction date'],
            'Description': ['description', 'desc', 'memo', 'payee', 'details', 'particulars', 'name', 'transaction'],
            'Amount': ['amount', 'cost', 'value', 'price', 'spending', 'withdrawal', 'deposit', 'debit', 'credit'],
            'Category': ['category', 'type', 'group', 'classification']
        }

        best_row_idx = 0
        max_matches = 0
        
        for i, row in sample_df.iterrows():
            row_str = [str(v).lower() for v in row.values if pd.notna(v) and str(v).strip() != '']
            matches = 0
            for expected_col, aliases in expected_mapping.items():
                if any(any(alias in cell for cell in row_str) for alias in aliases):
                    matches += 1
            if matches > max_matches:
                max_matches = matches
                best_row_idx = i
                
        # Reload the file with the identified header row
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, header=best_row_idx)
        
    except Exception as e:
        st.error(f"Failed to read the file. Error: {e}")
        return None, None, None

    # 2. Extract specific columns safely
    extracted_data = {}
    missing_cols = []
    
    # We pick exactly one column for each expected column to avoid duplicate axis issues
    for expected_col, aliases in expected_mapping.items():
        matched_col = None
        
        # Priority 1: Exact match
        for col in df.columns:
            if str(col).strip().lower() == expected_col.lower():
                matched_col = col
                break
                
        # Priority 2: Substring / Alias match
        if not matched_col:
            for col in df.columns:
                cl = str(col).strip().lower()
                if any(alias in cl for alias in aliases):
                    matched_col = col
                    break
                    
        if matched_col:
            # If CSV had exact identical column headers, df[matched_col] returns a DataFrame. Take first one.
            col_data = df[matched_col]
            if isinstance(col_data, pd.DataFrame):
                col_data = col_data.iloc[:, 0]
            extracted_data[expected_col] = col_data
        else:
            missing_cols.append(expected_col)

    required_missing = [c for c in ['Date', 'Amount', 'Description'] if c in missing_cols]
    if required_missing:
        st.error(f"Could not find required columns loosely matching: {', '.join(required_missing)}.")
        return None, None, None

    # Replace df with ONLY our clean target columns
    df = pd.DataFrame(extracted_data)
    
    # 2.5 Auto-Categorize if 'Category' is missing
    if 'Category' not in df.columns:
        def auto_categorize(desc):
            desc = str(desc).lower()
            if any(w in desc for w in ['uber', 'lyft', 'taxi', 'transit', 'mta', 'gas', 'shell', 'chevron', 'exxon', 'mobil', 'airlines']): return 'Transport'
            if any(w in desc for w in ['restaurant', 'cafe', 'coffee', 'doordash', 'uber eats', 'starbucks', 'mcdonald', 'burger', 'pizza', 'grubhub']): return 'Dining'
            if any(w in desc for w in ['walmart', 'target', 'amazon', 'grocery', 'whole foods', 'safeway', 'kroger', 'trader joe', 'costco']): return 'Groceries & Shopping'
            if any(w in desc for w in ['netflix', 'spotify', 'hulu', 'apple', 'gym', 'planet fitness', 'disney', 'hbo']): return 'Entertainment & Subscriptions'
            if any(w in desc for w in ['pharmacy', 'cvs', 'walgreens', 'health', 'doctor', 'hospital', 'medical']): return 'Healthcare'
            if any(w in desc for w in ['payment', 'transfer', 'zelle', 'venmo', 'paypal', 'credit card', 'atm', 'deposit', 'withdrawal']): return 'Transfer & Payment'
            return 'Other'
        df['Category'] = df['Description'].apply(auto_categorize)

    # 3. Proper Datetime Conversion
    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
    except Exception as e:
        st.error("Failed to parse 'Date' column format.")
        return None, None, None
        
    # Standardize numeric values
    if df['Amount'].dtype == 'object':
        df['Amount'] = df['Amount'].astype(str).str.replace(r'[\$,]|Rs\.?|NPR', '', regex=True)
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

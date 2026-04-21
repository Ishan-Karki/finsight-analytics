import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "finance.db")

def init_db():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            amount REAL,
            category TEXT,
            raw_metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_transactions(df):
    conn = sqlite3.connect(DB_PATH)
    # Mapping dataframe columns to table columns
    # We use 'date' as a string for SQLite storage
    df_to_save = df.copy()
    if 'Date' in df_to_save.columns:
        df_to_save['date'] = df_to_save['Date'].dt.strftime('%Y-%m-%d')
    
    # We'll rename for the SQL table
    df_to_save = df_to_save.rename(columns={
        'Description': 'description',
        'Amount': 'amount',
        'Category': 'category'
    })
    
    # Keep only target columns
    cols = ['date', 'description', 'amount', 'category']
    df_to_save = df_to_save[cols]
    
    df_to_save.to_sql('transactions', conn, if_exists='append', index=False)
    conn.close()

def get_all_transactions():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC", conn)
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

def get_transaction_summary():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT category, SUM(amount) as total FROM transactions GROUP BY category", conn)
    conn.close()
    return df

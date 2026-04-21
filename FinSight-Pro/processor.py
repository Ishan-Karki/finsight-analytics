import pandas as pd
import streamlit as st
import numpy as np
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def _extract_json_array(response_text: str):
    """
    Safely extract the first valid JSON array from model output.
    Handles markdown wrappers and trailing non-JSON text.
    """
    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    decoder = json.JSONDecoder()

    # Try direct parse first.
    try:
        parsed, _ = decoder.raw_decode(cleaned)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Fallback: locate first '[' and decode from there.
    start = cleaned.find('[')
    if start == -1:
        raise ValueError("No JSON array found in AI response.")

    parsed, _ = decoder.raw_decode(cleaned[start:])
    if not isinstance(parsed, list):
        raise ValueError("AI response did not contain a valid JSON array.")
    return parsed

def process_with_ai(uploaded_file):
    """
    Sends the uploaded file to Gemini to extract financial transactions into a structured JSON format.
    Handles CSV, TXT, PDF, and images.
    """
    if not api_key:
        st.error("GEMINI_API_KEY is missing from the .env file. Please add your Gemini API Key to continue.")
        return None, None, None

    try:
        # Prepare the file for Gemini
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name.lower()
        
        # Determine mime type
        if file_name.endswith('.pdf'):
            mime_type = 'application/pdf'
        elif file_name.endswith('.csv'):
            mime_type = 'text/csv'
        elif file_name.endswith('.txt'):
            mime_type = 'text/plain'
        elif file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
            mime_type = 'image/jpeg'
        elif file_name.endswith('.png'):
            mime_type = 'image/png'
        else:
            mime_type = 'text/plain'

        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        prompt = """
        You are an expert financial data extractor. I am providing you with a file (could be an image of a receipt, a PDF statement, or a messy CSV/TXT file).
        Please extract all financial transactions and return ONLY a valid JSON array of objects. 
        Each object MUST have these exact keys:
        - "Date": The transaction date in YYYY-MM-DD format.
        - "Description": A brief string describing the payee or transaction.
        - "Amount": The monetary amount as a positive number (float). Ignore currency symbols.
        - "Category": Categorize exactly as 'Deposit' (if money is coming in/credit) or 'Withdraw' (if money is going out/debit).
        - "Balance": Closing/running balance visible after this transaction in the statement. Use a number if available, otherwise null.
        
        Do NOT write markdown code blocks like ```json ... ```. Just return the raw JSON array starting with '[' and ending with ']'.
        """
        
        contents = [
            {"mime_type": mime_type, "data": file_bytes},
            prompt
        ]
        
        response = model.generate_content(contents)
        response_text = response.text.strip()

        json_data = _extract_json_array(response_text)
        
        if not json_data or not isinstance(json_data, list):
            st.error("No transactions found or incorrect format returned by AI.")
            return None, None, None
            
        df = pd.DataFrame(json_data)
        
        # Ensure correct column types
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0.0)
        df['Description'] = df['Description'].fillna("Unknown")
        df['Category'] = df['Category'].fillna("Uncategorized")
        if 'Balance' in df.columns:
            df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce')
        else:
            df['Balance'] = np.nan
        
        # Calculate summaries
        category_totals = df.groupby('Category', as_index=False)['Amount'].sum().sort_values(by='Amount')
        
        daily_trend = df.groupby(df['Date'].dt.date)['Amount'].sum().reset_index()
        daily_trend.rename(columns={'index': 'Date'}, inplace=True)
        # Rename date back if needed
        if 'Date' not in daily_trend.columns and len(daily_trend.columns) > 0:
            daily_trend.columns = ['Date', 'Amount']
            
        daily_trend = daily_trend.sort_values(by='Date')
        
        return df, category_totals, daily_trend

    except Exception as e:
        st.error(f"Error during AI processing: {str(e)}")
        return None, None, None


def chat_with_data(user_query, history_df):
    """
    Uses Gemini to answer questions about the transaction history.
    """
    if not api_key:
        return "I'm sorry, but it looks like the Gemini API Key is missing. Please contact support."

    try:
        # Prepare a summary of the data to keep it within context limits if needed, 
        # but for typical personal history, the whole CSV is usually fine for Gemini 1.5 Flash.
        # We'll convert the DF to a compact CSV-like string for the prompt.
        data_context = history_df.to_csv(index=False)
        
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        system_prompt = f"""
        You are 'FinSight AI', a specialized personal finance assistant for the SpendWise-Analytics / FinSight-Pro app.
        You have access to the user's transaction history provided below in CSV format.
        
        USER DATA:
        {data_context}
        
        GUIDELINES:
        1. Answer questions based ONLY on the provided data.
        2. Be concise but helpful. Use NPR (Rs.) for currency.
        3. Transactions are categorized as 'Deposit' or 'Withdraw'.
        4. If you're asked for summaries, give them.
        5. If you don't find the answer, politely say you don't have that data.
        6. Format your response with markdown for better readability (bolding, lists, etc.).
        7. Today's date is {pd.Timestamp.now().strftime('%Y-%m-%d')}.
        """
        
        response = model.generate_content([system_prompt, user_query])
        return response.text.strip()
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"


import streamlit as st
import processor

def render_chatbot():
    st.header("🤖 Chat with FinSight AI")
    st.write("Your AI assistant knows the details of all transactions uploaded in this session.")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is my biggest expense category?"):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Analyzing current session data..."):
            # Use session-based transactions instead of persistent DB
            session_history = st.session_state.get("session_transactions", None)
            
            if session_history is not None and not session_history.empty:
                response = processor.chat_with_data(prompt, session_history)
            else:
                response = "I don't have any transaction data for this session yet. Please upload a file first!"
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

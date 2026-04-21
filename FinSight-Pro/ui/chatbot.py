import streamlit as st
import processor
import database

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

        with st.spinner("Analyzing data history..."):
            # Fetch both session and lifetime history
            session_history = st.session_state.get("session_transactions", pd.DataFrame())
            lifetime_history = database.get_all_transactions()
            
            # Combine for full context, dropping duplicates if any
            full_context = pd.concat([session_history, lifetime_history.rename(columns={
                'date': 'Date', 'description': 'Description', 'amount': 'Amount', 'category': 'Category'
            })]).drop_duplicates().reset_index(drop=True)
            
            if not full_context.empty:
                response = processor.chat_with_data(prompt, full_context)
            else:
                response = "I don't have any transaction data for this session or your history yet. Please upload a file first!"
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

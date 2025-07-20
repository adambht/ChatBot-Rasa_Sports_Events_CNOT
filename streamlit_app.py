import streamlit as st
import requests

# Set your Rasa server URL
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

# Reset the session state when the app starts
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.user_input = ""
    st.session_state.chat_history = []

def get_response(user_input):
    response = requests.post(RASA_SERVER_URL, json={"sender": "user", "message": user_input})
    if response.ok:
        return response.json()
    else:
        return [{"text": "Error: Unable to reach the chatbot."}]

# Streamlit app layout
st.title("ChatChamp")
st.write("Talk to the chatbot!")

# Input text box for user messages
user_input = st.text_input("You:", st.session_state.user_input)

if st.button("Send"):
    if user_input:
        # Get the response from the bot
        responses = get_response(user_input)

        # Update chat history with user message
        st.session_state.chat_history.append(f"You: {user_input}")

        # Append the bot's response to chat history with line breaks
        for message in responses:
            bot_message = message['text'].replace("  ", "  \n")  # Replace two spaces with newlines
            st.session_state.chat_history.append(f"Bot: {bot_message.strip()}")  # Add to chat history

        # Clear input box for the next message
        st.session_state.user_input = ""
    else:
        st.write("Please enter a message.")

# Display chat history with custom styling
for message in st.session_state.chat_history:
    if message.startswith("You:"):
        st.markdown(
            f"<div style='text-align: right; margin: 10px; padding: 10px; background-color: #FF6500; border-radius: 10px;'>{message}</div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='text-align: left; margin: 10px; padding: 10px; background-color: #1E3E62; border-radius: 10px;'>{message}</div>",
            unsafe_allow_html=True)

import streamlit as st
import helpers.sidebar
import asyncio
from services import prompts
from helpers import util

st.set_page_config(
    page_title="Quick Chat",
    page_icon="💬",
    layout="wide"
)

helpers.sidebar.show()

st.header("Quick Chat")
st.write("Get instant answers to your (not too) specific coding questions.")
ask_book = st.checkbox("Use The Pragmatic Programmer as context.", value=False)

# Ensure the session state is initialized
if "messages" not in st.session_state:
    initial_messages = [{"role": "system",
                         "content": prompts.quick_chat_system_prompt()}]
    st.session_state.messages = initial_messages
    st.session_state.evidence = None  # Initialize evidence state


# Print all messages in the session state
for message in [m for m in st.session_state.messages if m["role"] != "system"]:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# Display evidence if available
if "evidence" in st.session_state and st.session_state.evidence:
    evidence = st.session_state.evidence
    with st.chat_message(message["role"], avatar="🔎") :
        with st.expander(f"See Page {evidence['page_number']}", expanded=False):
            st.image(evidence["content"], caption=f"Page Number {evidence['page_number']}", use_column_width=True)

# Chat with the LLM, and update the messages list with the response.
# Handles the chat UI and partial responses along the way.
async def chat(messages):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        messages = await util.run_conversation(messages, message_placeholder)
        st.session_state.messages = messages

    if not ask_book:
        st.session_state.evidence = None  # Clear evidence
    return messages


# React to the user prompt
if prompt := st.chat_input("Ask a coding or software engineering question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    if ask_book:
        asyncio.run(util.ask_book(st.session_state.messages, st.empty()))
        st.rerun()
    else:
        asyncio.run(chat(st.session_state.messages))
        st.rerun()
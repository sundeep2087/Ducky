import io
from typing import List, Dict
import pandas
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import services.llm
from services import rag
from services import prompts


async def run_conversation(messages: List[Dict[str, str]], message_placeholder: DeltaGenerator) \
        -> List[Dict[str, str]]:
    full_response = ""
    message_placeholder.markdown("Thinking...")
    chunks = services.llm.converse(messages)
    chunk = await anext(chunks, "END OF CHAT")
    while chunk != "END OF CHAT":
        print(f"Received chunk from LLM service: {chunk}")
        if chunk.startswith("EXCEPTION"):
            full_response = ":red[We are having trouble generating advice. Please wait a minute and try again.]"
            print(f"Exception occurred: {chunk}")
            break
        full_response = full_response + chunk
        message_placeholder.markdown(full_response + "▌")
        chunk = await anext(chunks, "END OF CHAT")
    message_placeholder.markdown(full_response)
    messages.append({"role": "assistant", "content": full_response})
    return messages


async def run_prompt(prompt: str,
                     message_placeholder: DeltaGenerator) \
        -> List[Dict[str, str]]:
    messages = services.llm.create_conversation_starter(prompt)
    messages = await run_conversation(messages, message_placeholder)
    return messages


def copy_as_csv_string(data_frame: pandas.DataFrame) -> str:
    # Convert DataFrame to CSV-like string
    csv_string_io = io.StringIO()
    data_frame.to_csv(csv_string_io, index=False, sep=',')

    # Get the CSV data from the StringIO object
    return csv_string_io.getvalue()


# async def ask_book(messages: List[Dict[str, str]], message_placeholder: DeltaGenerator) -> List[Dict[str, str]]:
#     user_query = messages[-1]['content']
#     context, page_number, image_file_name = rag.get_closest_context_and_image(user_query)
#     prompt = prompts.quick_chat_with_semantic_search(user_query, context)
#
#     messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(user_query)
#
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         messages = await run_conversation(messages, message_placeholder)
#         st.session_state.messages = messages
#
#     # Add evidence context to the session state messages
#     evidence_message = {
#         "role": "evidence",
#         "content": image_file_name,
#         "page_number": int(page_number)
#     }
#     st.session_state.messages.append(evidence_message)
#
#     return messages


async def ask_book(messages: List[Dict[str, str]], message_placeholder: DeltaGenerator) -> List[Dict[str, str]]:
    user_query = messages[-1]['content']
    context, page_number, image_file_name = rag.get_closest_context_and_image(user_query)
    prompt = prompts.quick_chat_with_semantic_search(user_query, context)

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # Get the response from the LLM
        messages = await run_conversation(messages, message_placeholder)
        st.session_state.messages = messages

    # Store evidence separately in session state without adding to messages
    st.session_state.evidence = {
        "content": image_file_name,
        "page_number": int(page_number)
    }

    return messages

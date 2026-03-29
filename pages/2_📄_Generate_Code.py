import re
import streamlit as st
import asyncio
import io
import os
import pathlib
from os.path import isfile, join
import pandas as pd
import helpers.sidebar
import services.llm
import helpers.util
import traceback
from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES
from helpers import util
from services import prompts
import markdown_it

helpers.sidebar.show()

# ================================================================================== #
# ============================== Helper Functions ================================== #
# ================================================================================== #

def reset_state():
    st.session_state.mode = None
    st.session_state.code = ""
    st.session_state.explanation = ""
    st.session_state.editor_id = 0
    st.session_state.debug_requested = False
    st.session_state.error_message = ""
    st.rerun()


# ==================================================================================== #
# ============================== Page layout: Start ================================== #
# ==================================================================================== #


# Horizontal Buttons layout for review, debug, modify and reset
# Empty code on first run
if 'mode' not in st.session_state:
    st.session_state.mode = None

if "code" not in st.session_state:
    st.session_state.code = ""

if "explanation" not in st.session_state:
    st.session_state.explanation = ""

if "editor_id" not in st.session_state:
    st.session_state.editor_id = 0

col1, col2, col3, col_spacer, col_reset = st.columns([1, 1, 1, 4.0, 1])

# Set session to respective mode based on clicked button.
with col1:
    if st.button("🔍 Review"):
        st.session_state.mode = "review"
with col2:
    if st.button("🐞 Debug"):
        st.session_state.mode = "debug"
with col3:
    if st.button("✏️ Modify"):
        st.session_state.mode = "modify"
with col_reset:
    if st.button("🔄️ Reset"):
        reset_state()


# Default Editor options
EDITOR_KEY_PREFIX = "ace-editor"
INITIAL_CODE = st.session_state.code


# Display the Ace editor
code = st_ace(value=INITIAL_CODE,
        language=st.sidebar.selectbox("Language mode", options=LANGUAGES, index=121),
        placeholder="Write your code here...",
        theme=st.sidebar.selectbox("Theme", options=THEMES, index=2),
        keybinding=st.sidebar.selectbox(
            "Keybinding mode", options=KEYBINDINGS, index=3
        ),
        font_size=st.sidebar.slider("Font size", 5, 24, 14),
        tab_size=st.sidebar.slider("Tab size", 1, 8, 4),
        wrap=st.sidebar.checkbox("Wrap lines", value=False),
        show_gutter=st.sidebar.checkbox("Show gutter", value=True),
        show_print_margin=st.sidebar.checkbox("Show print margin", value=True),
        auto_update=st.sidebar.checkbox("Auto update", value=True),
        readonly=st.sidebar.checkbox("Read only", value=False),
        key=f"{EDITOR_KEY_PREFIX}-{st.session_state.editor_id}",
        height=300,
        min_lines=12,
        max_lines=20
    )

st.session_state.code = code
st.html("<hr>")
st.write(st.session_state.explanation)
st.html("<hr>")


# ============================================================================= #
# ============================== Review Code ================================== #
# ============================================================================= #


# Update the session state with the current code
st.session_state.code = code

if st.session_state.mode == "review":
    if st.session_state.code == "" or st.session_state.code is None:
        st.markdown("Please enter code and click review to obtain feedback!")
    else:
        st.session_state.explanation = ""
        code_to_review = st.session_state.code
        # review_prompt = prompts.review_prompt(code_to_review)
        # response = asyncio.run(util.run_prompt(prompts.review_prompt(code_to_review), st.empty()))
        # explanation = response[0]["content"]
        # st.session_state.explanation = explanation
        # st.session_state.mode = None
        review_prompt = services.prompts.review_prompt(code_to_review)
        messages = services.llm.create_conversation_starter(services.prompts.system_learning_prompt())
        messages.append({"role": "user", "content": review_prompt})
        asyncio.run(util.run_conversation(messages, st.empty()))


# ============================================================================ #
# ============================== Debug Code ================================== #
# ============================================================================ #


if st.session_state.mode == "debug":
    st.session_state.explanation = ""

    # Error input area
    error_string = st.text_area("⛓️‍💥 Error Message:", placeholder="Enter the error message here...")

    if st.button("🔧 Debug Code"):
        if st.session_state.code == "":
            st.markdown("Please enter code in the above text area to debug!")
        elif error_string == "":
            st.markdown("Please enter an error message!")
        else:
            code_to_debug = st.session_state.code
            # debug_prompt = prompts.debug_prompt(code_to_debug, error_string)
            response = asyncio.run(util.run_prompt(prompts.debug_prompt(code_to_debug, error_string), st.empty()))

            # Extract modified code
            code_pattern = r"```python\n(.*?)\n```"
            code_match = re.search(code_pattern, response[1]["content"], re.DOTALL)

            if code_match:
                code = code_match.group(1)
                modified_code = "# Modified code \n" + code
                st.session_state.code = modified_code
                st.markdown("### Modified Code:")
                st.code(modified_code, language='python')
            else:
                st.session_state['code'] = None

            # Extract explanation
            explanation_pattern = r"!!!Explanation\n(.*?)(?=\n{2,}|\Z)"
            explanation_match = re.search(explanation_pattern, response[1]["content"], re.DOTALL)
            if explanation_match:
                st.session_state['explanation'] = "### Explanation: \n" + explanation_match.group(1)
                st.markdown(st.session_state['explanation'])
            else:
                st.session_state['explanation'] = "No explanation provided."

            st.session_state.editor_id += 1
            st.rerun()


# ============================================================================= #
# ============================== Modify Code ================================== #
# ============================================================================= #


if st.session_state.mode == "modify":
    st.session_state.explanation = ""
    user_request = st.chat_input(placeholder="What would you like to create and modify...?")

    if user_request:
        # modify_code_prompt = prompts.modify_code_prompt(user_request)
        response = asyncio.run(util.run_prompt(prompts.modify_code_prompt(st.session_state.code, user_request), st.empty()))
        # Extract modified code
        code_pattern = r"```python\n(.*?)\n```"
        code_match = re.search(code_pattern, response[1]["content"], re.DOTALL)
        if code_match:
            code = code_match.group(1)
            modified_code = "# Modified code \n" + code
            st.session_state.code = modified_code
            st.markdown("### Modified Code:")
            st.code(modified_code, language='python')
        else:
            st.session_state['code'] = None
        # Extract explanation
        explanation_pattern = r"!!!Explanation\n(.*?)(?=\n{2,}|\Z)"
        explanation_match = re.search(explanation_pattern, response[1]["content"], re.DOTALL)
        if explanation_match:
            st.session_state['explanation'] = "### Explanation of Modifications: \n" + explanation_match.group(1)
            st.markdown(st.session_state['explanation'])
        else:
            st.session_state['explanation'] = "No explanation provided."
        st.session_state.editor_id += 1
        st.rerun()

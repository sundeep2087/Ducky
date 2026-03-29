import asyncio
import os

import streamlit as st
from asyncio import sleep

import helpers.sidebar
import helpers.util

from aitools_autogen.blueprint_project9 import MLWebAppBlueprint
# from aitools_autogen.blueprint_generate_core_client import CoreClientTestBlueprint
from aitools_autogen.config import llm_config_openai as llm_config
from aitools_autogen.utils import clear_working_dir
from streamlit_file_browser import st_file_browser

st.set_page_config(
    page_title="ML WebApp Generator",
    page_icon="📄",
    layout="wide"
)

# Show sidebar
helpers.sidebar.show()

if st.session_state.get("blueprint", None) is None:
    st.session_state.blueprint = MLWebAppBlueprint()

# Explanation for the users
st.markdown("""
# Welcome to UI Code Generator!

This application helps you quickly generate a **front-end code** for your machine learning models! Whether you're working with a classification, regression, or any other model, this tool will help you turn your Python code and problem description into a web interface that users can interact with.

#### What do you need to upload?

To get started, please upload two things:
1. **Python Code URL**: A link to the Python code file that contains various ML models you are experimenting with and the related logic.
2. **Metadata URL**: A link to the markdown file describing the problem, dataset, and feature explanations.

Sample Files to test the app:
- [Python Code](https://raw.githubusercontent.com/sundeep2087/sample_datasets/refs/heads/main/titanic/titanic_survival_prediction.py)
- [Metadata](https://raw.githubusercontent.com/sundeep2087/sample_datasets/refs/heads/main/titanic/metadata.md)

These URLs will help the application understand your machine learning problem and automatically generate HTML, CSS, and, JavaScript code.

#### What does this app help with?

This app automates the process of creating a **user-friendly web interface** for your ML models. It generates:
- A webpage for introducing your ML problem.
- Pages explaining your dataset, features, and the models you’ve used.
- A prediction page where users can input data and get model predictions.

It’s perfect for anyone who wants to quickly make their ML model accessible via a web browser—no need for manual web development!

""")

async def run_blueprint(seed: int = 42, python_code_url: str = "", metadata_url: str = "") -> str:
    await sleep(3)
    llm_config["seed"] = seed

    # Generate message with Python code URL and metadata URL
    task = f"""
    I want to create a web application using HTML, CSS, JavaScript, and Flask for my machine learning models. Here is the python code and metadata URLs.
        Python Code - {python_code_url}
        Metadata - {metadata_url}
    """

    # Pass the generated task to the blueprint
    await st.session_state.blueprint.initiate_work(message=task)
    return st.session_state.blueprint.summary_result


blueprint_ctr, parameter_ctr = st.columns(2, gap="large")
with blueprint_ctr:
    st.markdown("# Run Blueprint")

    # Allow users to input URLs for Python code and metadata
    python_code_url_input = st.text_input("Enter the URL for the Python code:",
                                          placeholder="https://example.com/your_python_code.py")
    metadata_url_input = st.text_input("Enter the URL for the metadata:",
                                       placeholder="https://example.com/metadata.md")

    agents = st.button("Start the Agents!", type="primary")

with parameter_ctr:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### Other Options")
    clear = st.button("Clear the autogen cache...&nbsp; ⚠️", type="secondary")
    seed = st.number_input("Enter a seed for the random number generator:", value=42)

results_ctr = st.empty()

if clear:
    with results_ctr:
        st.status("Clearing the agent cache...")
        clear_working_dir(".cache", "*")
        st.status("Cache cleared!")


if os.path.exists('aitools_autogen/coding'):
    st.markdown('# Generated Code')
    event = st_file_browser("aitools_autogen/coding", key='A')

if agents:
    with results_ctr:
        st.status("Running the Blueprint...")

    # Run the blueprint with the Python code and metadata URLs
    text = asyncio.run(run_blueprint(seed=seed, python_code_url=python_code_url_input, metadata_url=metadata_url_input))
    st.balloons()

    with results_ctr:
        st.markdown(text)

The following description helps set up the Ducky UI project on your local machine. 

## Setup

Make sure you have the following files in your project directory:
- `README.md`
- 🏠_Ducky.py
- .streamlit/config.toml
- data/ThePragmatticProgrammer.pdf
- data/audio/
- data/images/
- helpers/sidebar.py
- helpers/util.py
- requirements.txt
- pages/1_💬_Quick_Chat.py
- pages/2_📄_Generate_Code.py
- pages/3_🎓_Learning_Topics.py
- pages/4_🏞️_Images.py
- pages/5_️🎤_Voice_Chat.py
- services/llm.py
- services/prompts.py
- services/rag.py
- services/images.py
- services/audio.py
- static/logo.jpeg
- .env


## Execution
1. Create a virtual environment and activate it.  Below is  for unix-based system -
    ```python -m venv venv```
    ```source venv/bin/activate```
2. Install the required packages using the following command:
```pip install -r requirements.txt```
3. Run the following command to start the Ducky UI:
```streamlit run 🏠_Ducky.py```

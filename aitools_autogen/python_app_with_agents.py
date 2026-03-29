from autogen import ConversableAgent
import utils
from agents import WebPageScraperAgent, WebScraperAgent
from config import llm_config_openai as llm_config, WORKING_DIR

# Initialize agent0 as before
agent0 = ConversableAgent("a0",
    max_consecutive_auto_reply=0,
    llm_config=False,
    human_input_mode="NEVER")

# Initialize the WebScraperAgent
scraper_agent = WebScraperAgent()

# Initialize the summary agent to summarize the content
summary_agent = ConversableAgent("summary_agent",
                                 max_consecutive_auto_reply=6,
                                 llm_config=llm_config,
                                 human_input_mode="NEVER",
                                 code_execution_config=False,
                                 function_map=None,
                                 system_message="""
                                         You are an AI agent tasked with summarizing key points from the provided metadata and Python code. Your summary should cover the following areas:

                                         1. Problem Introduction:
                                            - Summarize the problem being solved by the machine learning model(s).
                                            - Provide an overview of the dataset used for training the model(s).
                                            - Describe the goal of the prediction task and any key challenges.

                                         2. Feature and Parameter Explanation:
                                            - Provide a detailed explanation of each feature/variable used in the model.
                                            - For each feature, describe its purpose, possible values, or types.
                                            - Explain how these features are relevant to the prediction task.

                                         3. Machine Learning Models:
                                            - Summarize the machine learning algorithms used in the Python code (e.g., Decision Tree, Random Forest, AdaBoost, Gradient Boosting, etc.).
                                            - For each model, explain its purpose, how it works, and why it was chosen for the task.
                                            - Describe any model evaluation techniques used (e.g., cross-validation, hyperparameter tuning) and how models are trained and validated.

                                         4. Model Interaction and User Input:
                                            - Describe how users will provide input parameters (e.g., numeric or categorical values).
                                            - Explain how the user will select from different models for generating predictions.
                                            - Clarify the output of the models and how predictions will be presented to the user.

                                         5. Web Application Pages and Functionality:
                                            - Page 1: Problem Introduction & Explanation
                                              - Provide an overview of the problem, why it is important and the dataset used for training the model. 
                                            - Page 2: Feature/Parameter and Models Overview 
                                              - List and explain each feature/parameter, its possible values, and its role in the prediction.
                                              - Explanation of each model used for solving this problem, how it works in general and its purpose.
                                            - Page 3: Model Selection and Prediction 
                                              - Allow users to input their parameters and choose from available models.
                                              - Display the prediction based on the user input and selected model.

                                         6. Additional Considerations:
                                            - Ensure that missing data is properly handled (e.g., imputation methods or handling missing values).
                                            - Describe how pre-trained models are stored and loaded for user interaction within the web application.
                                            - Clarify how the application will integrate with the models to provide predictions dynamically.

                                         Please generate a structured summary in **great detail** that includes all of the above points - the problem, dataset, features, models, and web application functionality. The summary should be suitable for use in creating a web application where users can interact with the model(s) and receive predictions based on their input.
                                         """)

# Define the task (URLs of Python code and metadata)
task = """
I want to create a web application using HTML, CSS, JavaScript, and Flask for my machine learning models. 
Here is the python code and metadata URLs.
    Python Code - https://raw.githubusercontent.com/sundeep2087/sample_datasets/refs/heads/main/titanic/titanic_survival_prediction.py
    Metadata - https://raw.githubusercontent.com/sundeep2087/sample_datasets/refs/heads/main/titanic/metadata.md
"""

agent0.initiate_chat(scraper_agent, True, message=task)
message = scraper_agent.last_message()
scraped_content = message["content"]

agent0.initiate_chat(summary_agent, True, message=scraped_content)
summary_message = agent0.last_message(summary_agent)

# Initialize the web app developer agent to create the web app from the summary
webapp_dev_agent = ConversableAgent("webapp_dev_agent",
    max_consecutive_auto_reply=6,
    llm_config=llm_config,
    human_input_mode="NEVER",
    code_execution_config=False,
    function_map=None,
    system_message="""
    You are an expert web development assistant, assisting users in creating full stack web applications using HTML, CSS, JavaScript, React and Flask.
    
    When you receive a message, you should expect that message to describe a Machine Learning problem statement, explanation of features used, different ML algorithms used to solve the problem, the different web pages that need to be created and their functionalities, and finally how users will interact with the web application.
    
    Your task is to generate the necessary UI and backend layers using HTML, CSS, JavaScript, React, and flask. 
    
    Enhance each web page of the application including as much information as you can in the relevant page. Do not leave out any part of the summary provided.
    
    All files must be generated in the webapp/UI directory.
    
    Enclose the code in triple backticks.
    
    Only generate the necessary code. Do not include any markdown, explanation, or extra lines like page names or descriptions inside code block.
    
    However, for each generated code block:
        - Ensure that the script type is clearly indicated.
        - Always start each code block with a preamble comment indicating the filename.
        - For example, use `<!-- filename: webapp/UI/<filename>.html -->` for HTML files.
        - Use `# filename: webapp/UI/<filename>.py` for Python files.
        - Use `// filename: webapp/UI/<filename>.js` for JavaScript files.
        - Use `/* filename: webapp/UI/<filename>.css */` for CSS files.
        - Ensure that the filename reflects the intended structure of the web application.
    
    Do not suggest incomplete code which requires users to modify. 
    Feel free to include multiple code blocks in one response. Do not ask users to copy and paste the result.
""")


agent0.initiate_chat(webapp_dev_agent, True, True, message=summary_message)
llm_message = agent0.last_message(webapp_dev_agent)["content"]

utils.save_code_files(llm_message, WORKING_DIR)
print(utils.summarize_files(WORKING_DIR))

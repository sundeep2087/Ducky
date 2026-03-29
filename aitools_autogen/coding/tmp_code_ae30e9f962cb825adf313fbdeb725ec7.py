

# Now, let's create the Streamlit app. This app will allow users to input data, send this data to the Flask API, and display the prediction.

# Create a new Python script for the Streamlit app:


# File path: webapp/streamlit_pages/predict_app.py

import streamlit as st
import requests
import json

# Assuming your Flask API endpoint for making predictions is as follows
FLASK_API_URL = "http://localhost:5000/predict"

# Function to send data to the Flask API and receive the prediction
def get_prediction(input_data):
    response = requests.post(FLASK_API_URL, json=input_data)
    prediction = response.json()
    return prediction

# Streamlit UI
def main():
    st.title("Machine Learning Model Prediction")

    # Assuming the model expects two input features for simplicity: 'feature1' and 'feature2'
    # Adjust these input fields based on your actual model's requirements
    feature1 = st.text_input("Feature 1", "Enter value")
    feature2 = st.text_input("Feature 2", "Enter value")

    # Button to make prediction
    if st.button("Predict"):
        input_data = {
            "feature1": feature1,
            "feature2": feature2
        }
        
        prediction = get_prediction(input_data)
        
        st.write(f"Prediction: {prediction}")

if __name__ == "__main__":
    main()
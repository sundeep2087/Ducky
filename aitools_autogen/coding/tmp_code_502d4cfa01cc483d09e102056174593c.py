

### Step 2: Create the Flask API

# Navigate to the `webapp/api` directory or create it if it doesn't exist, then create a new Python file for the Flask app, for example, `app.py`.


# webapp/api/app.py
from flask import Flask, request, jsonify
import joblib
import os
import pandas as pd

app = Flask(__name__)

# Load the trained model (adjust the filename as necessary)
MODEL_DIR = os.path.join(os.getcwd(), '..', 'models')
model_filename = 'best_model_RandomForest.joblib'  # Adjust based on your saved model
model_path = os.path.join(MODEL_DIR, model_filename)
model = joblib.load(model_path)

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            data = request.get_json()
            # Assuming data is a dictionary with input features
            df = pd.DataFrame(data, index=[0])
            prediction = model.predict(df)
            return jsonify({'prediction': prediction.tolist()})
        except Exception as e:
            return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
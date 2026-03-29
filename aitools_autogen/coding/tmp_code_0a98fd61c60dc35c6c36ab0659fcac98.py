

# Now, let's create the Python script:


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV
import joblib
import os

# Replace these URLs with the actual URLs of your datasets
train_data_url = 'train_data_url'
test_data_url = 'test_data_url'

# Directories for saving Python module and ML model
module_dir = 'webapp/training'
model_dir = 'webapp/models'

if not os.path.exists(module_dir):
    os.makedirs(module_dir)
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# Load datasets
train_data = pd.read_csv(train_data_url)
test_data = pd.read_csv(test_data_url)

# Assuming the last column is the target variable
X_train = train_data.iloc[:, :-1]
y_train = train_data.iloc[:, -1]
X_test = test_data.iloc[:, :-1]
y_test = test_data.iloc[:, -1]

# Preprocessing
numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns
categorical_features = X_train.select_dtypes(include=['object', 'bool']).columns

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

# Models to train
classifiers = {
    'RandomForest': RandomForestClassifier(),
    'SVM': SVC(),
    'LogisticRegression': LogisticRegression()
}

best_score = 0
best_classifier = None

for classifier_name, classifier in classifiers.items():
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', classifier)])
    
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    score = f1_score(y_test, y_pred, average='weighted')
    
    print(f"{classifier_name} F1-Score: {score}")
    
    if score > best_score:
        best_score = score
        best_classifier = classifier_name
        # Save the best model
        joblib.dump(pipeline, os.path.join(model_dir, f'best_model_{best_classifier}.joblib'))

print(f"Best classifier: {best_classifier} with F1-Score: {best_score}")

# Save this script as a Python module
script_content = """
# The content of this script
"""
with open(os.path.join(module_dir, 'training_module.py'), 'w') as module_file:
    module_file.write(script_content)
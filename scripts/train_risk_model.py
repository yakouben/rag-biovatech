"""
Train the ChronicCare Risk Assessment Decision Tree.
Uses synthetic data calibrated to Algerian epidemiological distributions.
"""
import os
import pickle
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path

def generate_algerian_dataset(n_samples=5000):
    """
    Generates a synthetic dataset for chronic disease risk in Algeria using only numpy.
    """
    np.random.seed(42)
    
    # 1. Age: Skewed slightly older
    age = np.random.normal(55, 15, n_samples)
    age = np.clip(age, 18, 95)
    
    # 2. Gender: 0 for Female, 1 for Male
    gender = np.random.choice([0, 1], n_samples, p=[0.51, 0.49])
    
    # 3. BMI
    bmi = np.random.normal(28, 5, n_samples)
    bmi = np.clip(bmi, 15, 50)
    
    # 4. Smoking
    smoking = np.zeros(n_samples)
    for i in range(n_samples):
        if gender[i] == 1: # Male
            smoking[i] = np.random.choice([0, 1], p=[0.70, 0.30])
        else: # Female
            smoking[i] = np.random.choice([0, 1], p=[0.95, 0.05])
            
    # 5. Blood Pressure
    systolic_bp = 110 + (age * 0.4) + ((bmi-25) * 0.8) + np.random.normal(0, 10, n_samples)
    diastolic_bp = 70 + (age * 0.2) + ((bmi-25) * 0.4) + np.random.normal(0, 5, n_samples)
    
    # 6. Fasting Glucose
    glucose = 80 + (age * 0.5) + ((bmi-25) * 2.0) + np.random.normal(0, 15, n_samples)
    
    # 7. Family History & Comorbidities
    family_history = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    comorbidities = np.random.choice([0, 1, 2], n_samples, p=[0.5, 0.3, 0.2])
    
    # 8. Labeling
    labels = []
    for i in range(n_samples):
        risk_score = 0
        if systolic_bp[i] > 160 or diastolic_bp[i] > 100: risk_score += 4
        elif systolic_bp[i] > 140 or diastolic_bp[i] > 90: risk_score += 2
        if glucose[i] > 200: risk_score += 5
        elif glucose[i] > 126: risk_score += 3
        elif glucose[i] > 100: risk_score += 1
        if age[i] > 65: risk_score += 2
        if bmi[i] > 30: risk_score += 2
        if smoking[i] == 1: risk_score += 2
        if family_history[i] == 1: risk_score += 1
        if comorbidities[i] >= 1: risk_score += 2
        
        if risk_score >= 7:
            labels.append(2)
        elif risk_score >= 3:
            labels.append(1)
        else:
            labels.append(0)
            
    # Combine into feature matrix
    X = np.column_stack([
        age, systolic_bp, diastolic_bp, glucose, bmi, smoking, family_history, comorbidities
    ])
    y = np.array(labels)
    
    return X, y

def train_model():
    print("Generating Algerian-calibrated dataset...")
    X, y = generate_algerian_dataset(10000)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training DecisionTreeClassifier...")
    clf = DecisionTreeClassifier(
        max_depth=10,
        min_samples_leaf=5,
        class_weight='balanced',
        random_state=42
    )
    
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    print(f"Model Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    
    # Save the model
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    model_path = models_dir / "risk_decision_tree.pkl"
    
    with open(model_path, "wb") as f:
        pickle.dump(clf, f)
    
    print(f"\nModel saved successfully to {model_path}")

if __name__ == "__main__":
    train_model()

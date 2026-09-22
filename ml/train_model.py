from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / 'data'
MODELS_DIR = PROJECT_ROOT / 'models'

# Set seed for reproducibility
np.random.seed(42)

def generate_synthetic_data(num_records=1000):
    """
    Generate a synthetic dataset for automobile fault diagnosis.
    Features: Symptoms (Binary), Vehicle Age, Mileage, Sensor Readings
    Target: Fault Class
    """
    
    # Define features
    symptoms = [
        'engine_vibration', 'engine_overheating', 'poor_mileage', 
        'starting_problem', 'check_engine_light', 'brake_noise', 
        'battery_problem', 'low_power', 'abnormal_sound'
    ]
    
    # Fault classes and their primary symptom associations
    fault_profiles = {
        'Engine Misfire': ['engine_vibration', 'low_power', 'check_engine_light'],
        'Battery Problem': ['starting_problem', 'battery_problem', 'check_engine_light'],
        'Cooling System Problem': ['engine_overheating', 'check_engine_light'],
        'Brake Pad Wear': ['brake_noise', 'abnormal_sound'],
        'Fuel System Problem': ['poor_mileage', 'low_power', 'starting_problem'],
        'Starter Problem': ['starting_problem', 'abnormal_sound'],
        'Sensor Problem': ['check_engine_light'],
        'Normal': []
    }
    
    data = []
    fault_classes = list(fault_profiles.keys())
    
    for _ in range(num_records):
        # Pick a random fault
        fault = np.random.choice(fault_classes, p=[0.15, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.25])
        
        # Initialize record
        record = {s: 0 for s in symptoms}
        
        # Add primary symptoms for the fault (with some noise)
        primary_symptoms = fault_profiles[fault]
        for s in primary_symptoms:
            if np.random.random() > 0.1: # 90% chance to have the primary symptom
                record[s] = 1
        
        # Add random noise (symptoms not related to the fault)
        for s in symptoms:
            if s not in primary_symptoms:
                if np.random.random() > 0.95: # 5% chance to have a random symptom
                    record[s] = 1
        
        # Numerical features
        # Vehicle age (0-20 years)
        age = np.random.randint(0, 21)
        record['vehicle_age'] = age
        
        # Mileage (depends on age)
        record['mileage'] = age * np.random.randint(5000, 15000) + np.random.randint(0, 5000)
        
        # Sensor readings (with correlations to faults)
        # Engine Temp (Normal: 85-95)
        temp = np.random.normal(90, 3)
        if fault == 'Cooling System Problem':
            temp += np.random.randint(15, 30)
        record['engine_temperature'] = round(temp, 1)
        
        # RPM (Normal Idle: 700-900)
        rpm = np.random.normal(800, 50)
        if fault == 'Engine Misfire':
            rpm += np.random.normal(0, 150)
        record['rpm'] = int(rpm)
        
        # Battery Voltage (Normal: 12.4-12.8)
        voltage = np.random.normal(12.6, 0.2)
        if fault == 'Battery Problem':
            voltage -= np.random.uniform(1.0, 2.5)
        record['battery_voltage'] = round(voltage, 2)
        
        record['fault'] = fault
        data.append(record)
    
    df = pd.DataFrame(data)
    return df

def train_and_evaluate():
    print("🚀 Phase 3: Machine Learning Training")
    
    # 1. Generate Dataset
    print("📊 Generating synthetic automobile fault dataset...")
    df = generate_synthetic_data(1500)
    
    # Save dataset
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data_path = DATA_DIR / 'dataset.csv'
    df.to_csv(data_path, index=False)
    print(f"✅ Dataset saved to {data_path}")
    
    # 2. Preprocessing
    X = df.drop('fault', axis=1)
    y = df['fault']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Train Decision Tree
    print("🌳 Training Decision Tree Classifier...")
    dt_model = DecisionTreeClassifier(random_state=42)
    dt_model.fit(X_train, y_train)
    
    # Evaluate Decision Tree
    y_pred_dt = dt_model.predict(X_test)
    dt_acc = accuracy_score(y_test, y_pred_dt)
    print(f"✅ Decision Tree Accuracy: {dt_acc:.4f}")
    
    # 4. Train Random Forest (Optional Comparison)
    print("🌲 Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Evaluate Random Forest
    y_pred_rf = rf_model.predict(X_test)
    rf_acc = accuracy_score(y_test, y_pred_rf)
    print(f"✅ Random Forest Accuracy: {rf_acc:.4f}")
    
    # 5. Save the best model (Random Forest usually)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / 'diagnosis_model.pkl'
    joblib.dump(rf_model, model_path)
    print(f"✅ Best model saved to {model_path}")
    
    # Save feature names for inference
    feature_names_path = MODELS_DIR / 'feature_names.pkl'
    joblib.dump(X.columns.tolist(), feature_names_path)
    print(f"✅ Feature names saved to {feature_names_path}")
    
    # 6. Detailed Report
    print("\n📝 Classification Report (Random Forest):")
    print(classification_report(y_test, y_pred_rf))
    
    return dt_acc, rf_acc

if __name__ == "__main__":
    train_and_evaluate()

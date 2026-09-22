import joblib
import pandas as pd
import numpy as np
import os
from pathlib import Path

class DiagnosisPredictor:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[1]
        self.model_path = project_root / 'models' / 'diagnosis_model.pkl'
        self.features_path = project_root / 'models' / 'feature_names.pkl'
        self.model = None
        self.feature_names = None
        self.load_model()

    def load_model(self):
        """Load the trained model and feature names"""
        if os.path.exists(self.model_path) and os.path.exists(self.features_path):
            self.model = joblib.load(self.model_path)
            self.feature_names = joblib.load(self.features_path)
            return True
        return False

    def predict(self, input_data):
        """
        Predict fault based on input symptoms and sensor data.
        input_data: dictionary containing symptoms and sensor readings
        """
        if self.model is None:
            return None

        # Prepare input features in the correct order
        input_row = []
        for feature in self.feature_names:
            val = input_data.get(feature, 0)
            # Convert symptom names from UI to dataset format if needed
            # For now, we assume the UI keys match the feature names
            input_row.append(val)

        # Create DataFrame for prediction
        X_input = pd.DataFrame([input_row], columns=self.feature_names)
        
        # Get prediction and probabilities
        prediction = self.model.predict(X_input)[0]
        probabilities = self.model.predict_proba(X_input)[0]
        confidence = np.max(probabilities) * 100
        
        # Define severity and recommendations (can be moved to a separate config/db later)
        fault_info = {
            'Engine Misfire': {
                'severity': 'HIGH',
                'causes': ['Spark plug issue', 'Ignition coil problem', 'Fuel injector malfunction'],
                'recommendation': 'Inspect ignition and fuel systems with a qualified technician.'
            },
            'Battery Problem': {
                'severity': 'MEDIUM',
                'causes': ['Battery discharge', 'Alternator failure', 'Corroded terminals'],
                'recommendation': 'Check battery terminals for corrosion. Test battery voltage. Replace if needed.'
            },
            'Cooling System Problem': {
                'severity': 'HIGH',
                'causes': ['Low coolant level', 'Thermostat failure', 'Water pump issue'],
                'recommendation': 'Stop the vehicle immediately and allow it to cool. Check coolant level and consult a technician.'
            },
            'Brake Pad Wear': {
                'severity': 'MEDIUM',
                'causes': ['Brake pads worn out', 'Brake rotor damage', 'Brake fluid contamination'],
                'recommendation': 'Replace brake pads and inspect rotors. Do not delay this service.'
            },
            'Fuel System Problem': {
                'severity': 'MEDIUM',
                'causes': ['Fuel pump failure', 'Clogged fuel filter', 'Fuel pressure regulator issue'],
                'recommendation': 'Have the fuel system inspected and cleaned by a professional.'
            },
            'Starter Problem': {
                'severity': 'HIGH',
                'causes': ['Battery discharge', 'Starter motor failure', 'Alternator issue'],
                'recommendation': 'Check battery voltage and connections. If problem persists, consult a technician.'
            },
            'Sensor Problem': {
                'severity': 'LOW',
                'causes': ['Faulty O2 sensor', 'Mass Air Flow sensor issue', 'Engine coolant sensor fault'],
                'recommendation': 'Perform a full OBD-II scan to identify the specific faulty sensor.'
            },
            'Normal': {
                'severity': 'LOW',
                'causes': ['No significant issues detected'],
                'recommendation': 'Continue regular maintenance schedule.'
            }
        }
        
        info = fault_info.get(prediction, {
            'severity': 'LOW',
            'causes': ['Unknown'],
            'recommendation': 'Consult a qualified mechanic.'
        })
        
        return {
            'fault': prediction,
            'confidence': round(confidence, 2),
            'severity': info['severity'],
            'causes': info['causes'],
            'recommendation': info['recommendation']
        }

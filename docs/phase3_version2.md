# Phase 3: Version 2 - Machine Learning Diagnosis

## What We Built

**Version 2** upgrades the diagnosis engine from simple rules to a **Machine Learning (ML)** model.

1. **Synthetic Dataset Generation**: Created a script (`ml/train_model.py`) that generates 1,500 realistic vehicle fault records.
   - **Features**: Symptoms (Engine vibration, Overheating, etc.) + Sensor Data (Temperature, RPM, Voltage) + Vehicle Stats (Age, Mileage).
   - **Target**: 8 Fault Classes (Engine Misfire, Battery Problem, Brake Wear, etc.).

2. **ML Model Training**:
   - **Decision Tree**: A beginner-friendly model that creates a "tree" of decisions.
   - **Random Forest**: An advanced model that combines multiple Decision Trees for better accuracy.
   - **Accuracy**: The Random Forest model achieved ~90% accuracy on our synthetic data.

3. **Inference Engine**: Created `ml/prediction.py` to handle real-time predictions with confidence scores.

4. **Updated UI**:
   - Added **Sensor Data Inputs**: Sliders and number inputs for Temperature, RPM, and Voltage.
   - Added **Diagnosis Mode Toggle**: Switch between "AI Model" and "Rule-Based" diagnosis.

## Why This Matters

Rule-based systems are hard to maintain as they grow. ML allows the system to:
- Learn patterns from data rather than hard-coded rules.
- Handle "fuzzy" or incomplete data (e.g., if a symptom is missing but sensor data is abnormal).
- Provide a **Confidence Score** based on mathematical probability.

## File Structure for Phase 3

```
automobile-ai-assistant/
├── app.py
├── data/
│   └── dataset.csv           # The generated training data
├── ml/
│   ├── train_model.py        # Dataset generation & training script
│   └── prediction.py         # The AI prediction logic
├── models/
│   ├── diagnosis_model.pkl   # The trained AI "brain"
│   └── feature_names.pkl     # List of features the model expects
├── docs/
│   ├── phase1_architecture.md
│   ├── phase2_version1.md
│   └── phase3_version2.md    # This file
```

## How to Run Version 2

### Step 1: Train the Model
(I have already done this for you, but here is the command if you want to re-run it)
```bash
python3 ml/train_model.py
```

### Step 2: Run the App
```bash
streamlit run app.py
```

## Testing Version 2

### Test Case 1: AI Diagnosis (Normal)
1. Register a vehicle.
2. Go to **"🔍 Diagnose Vehicle"**.
3. Select **NO symptoms**.
4. Set **Engine Temperature** to 90°C, **RPM** to 800, **Battery** to 12.6V.
5. Select **"AI Model (Random Forest)"** mode.
6. Click **"🔍 Diagnose Vehicle"**.
7. Expected Result: Predicted Fault: `Normal`, Confidence: High.

### Test Case 2: AI Diagnosis (Battery Problem)
1. Select symptom: **"Battery problem"**.
2. Set **Battery Voltage** to 10.5V.
3. Select **"AI Model (Random Forest)"** mode.
4. Click **"🔍 Diagnose Vehicle"**.
5. Expected Result: Predicted Fault: `Battery Problem`, Severity: `MEDIUM`.

### Test Case 3: AI Diagnosis (Cooling System)
1. Select symptom: **"Engine overheating"**.
2. Set **Engine Temperature** to 115°C.
3. Select **"AI Model (Random Forest)"** mode.
4. Click **"🔍 Diagnose Vehicle"**.
5. Expected Result: Predicted Fault: `Cooling System Problem`, Severity: `HIGH`.

## Key ML Concepts Explained

### 1. Decision Tree
Imagine a flow chart: "Is temperature > 100? Yes -> Is RPM > 2000? Yes -> Engine Overheating". That's a Decision Tree.

### 2. Random Forest
A "forest" of many Decision Trees. Each tree gives a "vote," and the majority vote becomes the final prediction. This is much more accurate and stable.

### 3. Training vs. Inference
- **Training**: Teaching the model using the `dataset.csv`. (Done once)
- **Inference**: Using the trained `diagnosis_model.pkl` to predict a fault for a new user. (Done every time you click "Diagnose")

### 4. Overfitting
If a model memorizes the training data too perfectly, it might fail on new, real-world data. We use a "Test Set" to ensure the model actually learns patterns, not just memorizes.

## Next Steps

Proceed to Phase 4 to implement the **SQLite Database** to permanently save your vehicle and diagnosis data!

# Phase 2: Version 1 - Vehicle Registration & Rule-Based Diagnosis

## What We Built

**Version 1** is a functional Streamlit application with the following features:

1. **Vehicle Registration Form**: Users can register their vehicle with details like registration number, manufacturer, model, year, fuel type, transmission type, mileage, and last service date.

2. **Symptom Selection Interface**: Users can select from 20+ predefined symptoms organized into 5 categories:
   - 🔧 Engine (6 symptoms)
   - ⛽ Fuel (3 symptoms)
   - 🛑 Brakes (3 symptoms)
   - ⚡ Electrical (3 symptoms)
   - 🔊 Sound (4 symptoms)

3. **Rule-Based Diagnosis Engine**: A simple rule-based system that maps symptom combinations to possible faults with:
   - Predicted fault name
   - Confidence score (0-100%)
   - Severity level (LOW, MEDIUM, HIGH, CRITICAL)
   - Possible causes (list)
   - Recommended actions

4. **Dashboard**: Displays vehicle information, total diagnoses, and last diagnosis timestamp.

5. **Diagnosis History**: Stores and displays all previous diagnoses with timestamps.

## Why This Matters

This version establishes the **foundation** of our application. It demonstrates:
- How to structure a Streamlit multi-page application
- How to manage session state (data persistence during user interaction)
- How to implement a simple rule-based diagnostic system
- How to organize UI components effectively

## File Structure for Phase 2

```
automobile-ai-assistant/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── docs/
│   ├── phase1_architecture.md
│   └── phase2_version1.md    # This file
```

## Installation & Setup

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Verify Installation
```bash
python3 -c "import streamlit; print('Streamlit installed successfully')"
```

## How to Run Version 1

### Command:
```bash
streamlit run app.py
```

### Expected Output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Your default web browser will open automatically. If not, manually navigate to `http://localhost:8501`.

## Testing Version 1

### Test Case 1: Vehicle Registration
1. Click on **"🚗 Vehicle Registration"** in the sidebar
2. Fill in the form with sample data:
   - Registration Number: `DL-01-AB-1234`
   - Manufacturer: `Hyundai`
   - Model: `i20`
   - Manufacturing Year: `2020`
   - Fuel Type: `Petrol`
   - Transmission Type: `Manual`
   - Current Mileage: `45000`
   - Last Service Date: `2024-01-15`
3. Click **"💾 Save Vehicle Information"**
4. Expected: Green success message "✅ Vehicle information saved successfully!"

### Test Case 2: Dashboard Display
1. Click on **"🏠 Dashboard"** in the sidebar
2. Expected: You should see:
   - "Vehicle Registered: ✅ Yes"
   - "Total Diagnoses: 0" (initially)
   - Vehicle information displayed in a table

### Test Case 3: Simple Diagnosis
1. Click on **"🔍 Diagnose Vehicle"** in the sidebar
2. Expand **"⚡ Electrical"** category
3. Check **"Battery problem"** and **"Warning light"**
4. Click **"🔍 Diagnose Vehicle"** button
5. Expected Results:
   - Predicted Fault: `Battery Problem`
   - Confidence: `90%`
   - Severity: `🟡 MEDIUM`
   - Possible Causes: Listed
   - Recommended Action: Displayed

### Test Case 4: Complex Diagnosis
1. Click on **"🔍 Diagnose Vehicle"** in the sidebar
2. Expand **"🔧 Engine"** category
3. Check **"Engine vibration"**, **"Poor acceleration"**, and **"Low engine power"**
4. Click **"🔍 Diagnose Vehicle"** button
5. Expected Results:
   - Predicted Fault: `Engine Misfire`
   - Confidence: `85%`
   - Severity: `🟠 HIGH`

### Test Case 5: Diagnosis History
1. After performing at least 2 diagnoses (Test Case 3 and 4)
2. Click on **"📋 Diagnosis History"** in the sidebar
3. Expected: A table showing all diagnoses with:
   - Timestamp
   - Vehicle
   - Symptoms
   - Predicted Fault
   - Confidence
   - Severity
   - Recommendation

## Common Beginner Errors & Solutions

### Error 1: "ModuleNotFoundError: No module named 'streamlit'"
**Cause**: Streamlit not installed
**Solution**:
```bash
pip install streamlit
```

### Error 2: "Port 8501 is already in use"
**Cause**: Another application is using port 8501
**Solution**:
```bash
streamlit run app.py --server.port 8502
```

### Error 3: "FileNotFoundError: [Errno 2] No such file or directory: 'app.py'"
**Cause**: Running command from wrong directory
**Solution**: Ensure you're in the `automobile-ai-assistant/` directory:
```bash
cd automobile-ai-assistant
streamlit run app.py
```

### Error 4: "No vehicle registered yet" message appears
**Cause**: Vehicle data not saved
**Solution**: Go to "🚗 Vehicle Registration", fill the form, and click "💾 Save Vehicle Information"

## Expected Output Examples

### Dashboard Page:
```
Vehicle Registered: ✅ Yes
Total Diagnoses: 2
Last Diagnosis: 2024-11-15 14:30:45

Current Vehicle Information:
registration_number  manufacturer  model  manufacturing_year  fuel_type  transmission_type  current_mileage  last_service_date
DL-01-AB-1234       Hyundai       i20    2020                Petrol     Manual             45000            2024-01-15
```

### Diagnosis Results:
```
Predicted Fault: Engine Misfire
Confidence: 85%
Severity: 🟠 HIGH

Possible Causes:
1. Spark plug issue
2. Ignition coil issue
3. Fuel injector issue

Recommended Action:
Inspect the ignition and fuel systems with a qualified technician.
```

## How to Proceed to Phase 3

Once you've tested Version 1 successfully:
1. Verify all test cases pass
2. Understand the rule-based diagnosis logic
3. Proceed to **Phase 3** where we'll:
   - Generate a synthetic automobile fault dataset
   - Train a Decision Tree ML model
   - Compare with Random Forest
   - Replace rule-based diagnosis with ML-based diagnosis

## Key Concepts Explained

### Session State
Streamlit's `st.session_state` is like the application's memory. It stores data (vehicle info, diagnosis history) so it persists as the user navigates between pages.

### Rule-Based Diagnosis
Instead of ML, we use predefined rules: "If user selects symptoms X and Y, then fault is Z with confidence C%". This is simple but limited to known symptom combinations.

### Severity Levels
- 🟢 **LOW**: Minor issue, can be addressed during routine maintenance
- 🟡 **MEDIUM**: Should be inspected soon, not immediately dangerous
- 🟠 **HIGH**: Requires prompt attention, affects vehicle safety or performance
- 🔴 **CRITICAL**: Stop driving immediately, seek professional help urgently

## Next Steps

Proceed to Phase 3 to implement Machine Learning-based diagnosis!

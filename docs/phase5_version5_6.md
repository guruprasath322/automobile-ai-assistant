# Phase 5: Version 5 & 6 - OBD-II Simulation & DTC Lookup

## What We Built

**Version 5 & 6** introduces vehicle telemetry through **OBD-II (On-Board Diagnostics)** simulation and a **DTC (Diagnostic Trouble Code)** lookup system.

1. **OBD-II Simulator (`obd/simulator.py`)**:
   - Generates real-time engine data like RPM, Temperature, Voltage, and Speed.
   - Includes **Fault Modes** (Normal, Misfire, Overheating, Low Voltage) to test how the system reacts to problems.

2. **DTC Lookup System**:
   - A database of common vehicle trouble codes (e.g., `P0301` for Cylinder 1 Misfire).
   - Provides descriptions, severity levels, and possible causes for each code.
   - Automatically detects codes during live monitoring.

3. **OBD-II Monitor Page**:
   - A new dashboard page to visualize live engine metrics.
   - Includes "Refresh" controls and the ability to send detected issues directly to the AI Diagnosis engine.

4. **Integrated Diagnosis**:
   - The **Diagnose Vehicle** page now has an **"Import Live OBD-II Data"** button.
   - You can automatically fill in sensor data and symptoms based on detected DTC codes.

## Why This Matters

OBD-II is the "language" of modern cars. By adding this module:
- **Automation**: The user doesn't have to manually type in RPM or Temperature; the system "reads" it from the car.
- **Accuracy**: DTC codes provide specific clues that help the AI model make better predictions.
- **Real-World Ready**: The simulation logic is designed to be easily replaced by a real ELM327 Bluetooth/USB adapter in the future.

## File Structure for Phase 5

```
automobile-ai-assistant/
├── app.py
├── data/
│   ├── dataset.csv
│   └── dtc_codes.csv         # New: DTC database
├── obd/
│   ├── simulator.py          # New: OBD-II simulation logic
│   └── obd_reader.py         # Placeholder for real hardware integration
├── docs/
│   ├── ...
│   └── phase5_version5_6.md  # This file
```

## How to Run Version 5 & 6

### Step 1: Run the App
```bash
streamlit run app.py
```

## Testing Version 5 & 6

### Test Case 1: Live Monitoring
1. Go to **"📡 OBD-II Monitor"** in the sidebar.
2. Select **"Normal"** mode and click **"🔄 Refresh Live Data"**.
3. Expected Result: Metrics show normal idle (RPM ~800, Temp ~90°C, Voltage ~12.6V).

### Test Case 2: Fault Simulation (Overheating)
1. In the OBD-II Monitor, select **"Cooling System Problem"** mode.
2. Click **"🔄 Refresh Live Data"**.
3. Expected Result: 
   - Engine Temperature jumps to >105°C.
   - DTC `P0117` is detected.
   - An error message appears with the description and severity.

### Test Case 3: Integrated Diagnosis
1. After detecting a fault in the Monitor (Test Case 2), click **"🛠️ Send to Diagnosis"**.
2. Navigate to the **"🔍 Diagnose Vehicle"** page.
3. Click **"📥 Import Live OBD-II Data"**.
4. Expected Result: The sliders for Temperature and the DTC text box are automatically filled with the fault data.

## Key OBD-II Concepts Explained

### 1. OBD-II (On-Board Diagnostics)
A standardized system that allows external devices to interface with a vehicle's computer system. It has been mandatory for all cars sold in the US since 1996 and India since 2010.

### 2. DTC (Diagnostic Trouble Code)
Five-character codes (like `P0301`) used by the vehicle's computer to identify specific problems.
- **P**: Powertrain (Engine/Transmission)
- **B**: Body
- **C**: Chassis
- **U**: Network

### 3. ELM327
The most common and affordable microchip used in OBD-II to USB/Bluetooth adapters. Our code is structured to work with the data format these adapters provide.

## Next Steps

Proceed to Phase 6 to implement the **Voice Assistant**, **Health Score**, and **PDF Report Generation**!

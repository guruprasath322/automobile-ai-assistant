"""
AI Automobile Health & Diagnosis Assistant - Version 1
Main Streamlit Application
This version includes: Vehicle Registration, Symptom Selection, and Rule-Based Diagnosis
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from pathlib import Path
from ml.prediction import DiagnosisPredictor
from database.database import AutomobileDB
from obd.simulator import OBDSimulator
from voice.speech import extract_symptoms_from_text
from reports.report_generator import generate_pdf_report
from utils.helpers import calculate_health_score

PROJECT_ROOT = Path(__file__).resolve().parent

# Initialize Database, Predictor, and OBD Simulator
db = AutomobileDB()
predictor = DiagnosisPredictor()
obd = OBDSimulator()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="AI Automobile Diagnosis Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'active_vehicle_reg' not in st.session_state:
        st.session_state.active_vehicle_reg = None
    
    # Load last registered vehicle if available
    all_vehicles = db.get_all_vehicles()
    if not st.session_state.active_vehicle_reg and not all_vehicles.empty:
        st.session_state.active_vehicle_reg = all_vehicles.iloc[0]['registration_number']

def save_vehicle_data(vehicle_info):
    """Save vehicle information to database"""
    db.save_vehicle(vehicle_info)
    st.session_state.active_vehicle_reg = vehicle_info['registration_number']
    st.success("✅ Vehicle information saved to database!")

def save_diagnosis_to_history(diagnosis_result):
    """Save diagnosis result to database"""
    diagnosis_record = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'vehicle': st.session_state.active_vehicle_reg or 'Unknown',
        'symptoms': diagnosis_result['symptoms'],
        'predicted_fault': diagnosis_result['fault'],
        'confidence': diagnosis_result['confidence'],
        'severity': diagnosis_result['severity'],
        'recommendation': diagnosis_result['recommendation']
    }
    db.save_diagnosis(diagnosis_record)

# ============================================================================
# RULE-BASED DIAGNOSIS ENGINE (Version 1)
# ============================================================================

def rule_based_diagnosis(selected_symptoms):
    """
    Simple rule-based diagnosis system.
    Maps symptom combinations to possible faults with confidence scores.
    """
    
    # Define diagnosis rules
    diagnosis_rules = {
        # Engine-related faults
        ('Engine vibration', 'Poor acceleration', 'Low engine power'): {
            'fault': 'Engine Misfire',
            'confidence': 85,
            'severity': 'HIGH',
            'causes': ['Spark plug issue', 'Ignition coil problem', 'Fuel injector malfunction'],
            'recommendation': 'Inspect ignition and fuel systems with a qualified technician.'
        },
        ('Engine vibration', 'Engine stalling'): {
            'fault': 'Fuel System Problem',
            'confidence': 75,
            'severity': 'MEDIUM',
            'causes': ['Fuel pump failure', 'Clogged fuel filter', 'Fuel pressure regulator issue'],
            'recommendation': 'Have the fuel system inspected and cleaned by a professional.'
        },
        ('Engine overheating',): {
            'fault': 'Cooling System Problem',
            'confidence': 80,
            'severity': 'HIGH',
            'causes': ['Low coolant level', 'Thermostat failure', 'Water pump issue'],
            'recommendation': 'Stop the vehicle immediately and allow it to cool. Check coolant level and consult a technician.'
        },
        ('Engine not starting',): {
            'fault': 'Starter Problem',
            'confidence': 70,
            'severity': 'HIGH',
            'causes': ['Battery discharge', 'Starter motor failure', 'Alternator issue'],
            'recommendation': 'Check battery voltage and connections. If problem persists, consult a technician.'
        },
        
        # Brake-related faults
        ('Brake noise', 'Brake vibration'): {
            'fault': 'Brake Pad Wear',
            'confidence': 88,
            'severity': 'MEDIUM',
            'causes': ['Brake pads worn out', 'Brake rotor damage', 'Brake fluid contamination'],
            'recommendation': 'Replace brake pads and inspect rotors. Do not delay this service.'
        },
        ('Weak braking',): {
            'fault': 'Brake System Problem',
            'confidence': 82,
            'severity': 'CRITICAL',
            'causes': ['Brake fluid leak', 'Air in brake lines', 'Master cylinder failure'],
            'recommendation': 'STOP driving immediately. Do not operate the vehicle. Seek professional help urgently.'
        },
        
        # Electrical-related faults
        ('Battery problem', 'Warning light'): {
            'fault': 'Battery Problem',
            'confidence': 90,
            'severity': 'MEDIUM',
            'causes': ['Battery discharge', 'Alternator failure', 'Corroded terminals'],
            'recommendation': 'Check battery terminals for corrosion. Test battery voltage. Replace if needed.'
        },
        ('Starter problem', 'Clicking sound'): {
            'fault': 'Electrical System Problem',
            'confidence': 78,
            'severity': 'MEDIUM',
            'causes': ['Low battery', 'Starter relay issue', 'Corroded connections'],
            'recommendation': 'Inspect battery and electrical connections. Test starter motor.'
        },
        
        # Fuel efficiency
        ('Poor mileage', 'High fuel consumption'): {
            'fault': 'Fuel System Problem',
            'confidence': 72,
            'severity': 'LOW',
            'causes': ['Faulty oxygen sensor', 'Clogged fuel injectors', 'Engine carbon buildup'],
            'recommendation': 'Clean fuel injectors and check oxygen sensor. Consider fuel system cleaning.'
        },
        
        # Sound-related faults
        ('Clicking sound',): {
            'fault': 'Electrical or Starter Problem',
            'confidence': 65,
            'severity': 'MEDIUM',
            'causes': ['Low battery', 'Starter motor issue', 'Bad connections'],
            'recommendation': 'Check battery voltage and connections first. Test starter if needed.'
        },
        ('Grinding sound',): {
            'fault': 'Brake or Transmission Problem',
            'confidence': 68,
            'severity': 'HIGH',
            'causes': ['Worn brake pads', 'Transmission issue', 'Differential problem'],
            'recommendation': 'Inspect brake system and transmission. Seek professional diagnosis.'
        },
        ('Knocking sound',): {
            'fault': 'Engine Knock / Detonation',
            'confidence': 70,
            'severity': 'MEDIUM',
            'causes': ['Low octane fuel', 'Carbon buildup', 'Ignition timing issue'],
            'recommendation': 'Use higher octane fuel. Have ignition timing checked by a technician.'
        },
        ('Whistling sound',): {
            'fault': 'Vacuum Leak or Belt Issue',
            'confidence': 62,
            'severity': 'LOW',
            'causes': ['Loose serpentine belt', 'Vacuum hose leak', 'Power steering pump issue'],
            'recommendation': 'Inspect belts and hoses. Tighten or replace as needed.'
        },
    }
    
    # Convert selected symptoms to tuple for matching
    symptoms_tuple = tuple(sorted(selected_symptoms))
    
    # Check for exact match
    if symptoms_tuple in diagnosis_rules:
        result = diagnosis_rules[symptoms_tuple].copy()
        result['symptoms'] = selected_symptoms
        return result
    
    # Check for partial matches (any subset of symptoms)
    best_match = None
    best_match_count = 0
    
    for rule_symptoms, rule_result in diagnosis_rules.items():
        matching_count = sum(1 for symptom in rule_symptoms if symptom in selected_symptoms)
        if matching_count > best_match_count:
            best_match = rule_result.copy()
            best_match_count = matching_count
    
    if best_match:
        best_match['symptoms'] = selected_symptoms
        return best_match
    
    # Default diagnosis if no rules match
    return {
        'fault': 'Unable to determine specific fault',
        'confidence': 30,
        'severity': 'LOW',
        'causes': ['Insufficient symptom data', 'Rare combination of symptoms'],
        'recommendation': 'Consult a qualified mechanic for professional diagnosis.',
        'symptoms': selected_symptoms
    }

# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    initialize_session_state()
    
    # Header
    st.markdown("# 🚗 AI Automobile Health & Diagnosis Assistant")
    st.markdown("**Version 1: Vehicle Registration & Rule-Based Diagnosis**")
    st.markdown("---")
    
    # Disclaimer
    st.warning(
        "⚠️ **Disclaimer**: This application provides AI-assisted predictions for educational purposes only. "
        "It is NOT a replacement for professional mechanical diagnosis. Always consult a qualified technician "
        "for critical vehicle issues."
    )
    
    # Sidebar Navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Select a page:",
        ["🏠 Dashboard", "🚗 Vehicle Registration", "🔍 Diagnose Vehicle", "📡 OBD-II Monitor", "📊 Vehicle Health", "📋 Diagnosis History"]
    )
    
    # ========================================================================
    # PAGE 1: DASHBOARD
    # ========================================================================
    if page == "🏠 Dashboard":
        st.subheader("Dashboard")
        
        active_vehicle = db.get_vehicle(st.session_state.active_vehicle_reg) if st.session_state.active_vehicle_reg else None
        history = db.get_diagnosis_history(st.session_state.active_vehicle_reg)
        
        if active_vehicle:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Active Vehicle", f"{active_vehicle['manufacturer']} {active_vehicle['model']}")
            with col2:
                st.metric("Total Diagnoses", len(history))
            with col3:
                last_diag = history.iloc[0]['timestamp'] if not history.empty else "None"
                st.metric("Last Diagnosis", last_diag)
            
            st.markdown("---")
            st.subheader("📊 Vehicle Details")
            st.dataframe(pd.DataFrame([active_vehicle]), use_container_width=True)
            
            if not history.empty:
                st.markdown("---")
                st.subheader("📈 Recent Health Status")
                last_fault = history.iloc[0]['predicted_fault']
                last_severity = history.iloc[0]['severity']
                
                severity_colors = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🟠', 'CRITICAL': '🔴'}
                st.info(f"Last detected issue: **{last_fault}** (Severity: {severity_colors.get(last_severity, '')} {last_severity})")
        else:
            st.info("📌 No vehicle registered yet. Please register a vehicle first.")
            
        # Vehicle Selector in Sidebar
        all_vehicles = db.get_all_vehicles()
        if not all_vehicles.empty:
            st.sidebar.markdown("---")
            st.sidebar.subheader("🚗 Switch Vehicle")
            selected_reg = st.sidebar.selectbox(
                "Select Vehicle:",
                all_vehicles['registration_number'].tolist(),
                index=all_vehicles['registration_number'].tolist().index(st.session_state.active_vehicle_reg) if st.session_state.active_vehicle_reg in all_vehicles['registration_number'].tolist() else 0
            )
            if selected_reg != st.session_state.active_vehicle_reg:
                st.session_state.active_vehicle_reg = selected_reg
                st.rerun()
    
    # ========================================================================
    # PAGE 2: VEHICLE REGISTRATION
    # ========================================================================
    elif page == "🚗 Vehicle Registration":
        st.subheader("Vehicle Registration Form")
        st.write("Enter your vehicle details below:")
        
        active_vehicle = db.get_vehicle(st.session_state.active_vehicle_reg) if st.session_state.active_vehicle_reg else {}
        
        with st.form("vehicle_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                registration_number = st.text_input(
                    "Vehicle Registration Number",
                    placeholder="e.g., DL-01-AB-1234",
                    value=active_vehicle.get('registration_number', '')
                )
                manufacturer = st.text_input(
                    "Manufacturer",
                    placeholder="e.g., Hyundai",
                    value=active_vehicle.get('manufacturer', '')
                )
                model = st.text_input(
                    "Model",
                    placeholder="e.g., i20",
                    value=active_vehicle.get('model', '')
                )
                manufacturing_year = st.number_input(
                    "Manufacturing Year",
                    min_value=1990,
                    max_value=datetime.now().year,
                    value=active_vehicle.get('manufacturing_year', 2020)
                )
            
            with col2:
                fuel_type = st.selectbox(
                    "Fuel Type",
                    ["Petrol", "Diesel", "CNG", "Hybrid", "Electric"],
                    index=["Petrol", "Diesel", "CNG", "Hybrid", "Electric"].index(
                        active_vehicle.get('fuel_type', 'Petrol')
                    )
                )
                transmission_type = st.selectbox(
                    "Transmission Type",
                    ["Manual", "Automatic", "CVT"],
                    index=["Manual", "Automatic", "CVT"].index(
                        active_vehicle.get('transmission_type', 'Manual')
                    )
                )
                current_mileage = st.number_input(
                    "Current Mileage (km)",
                    min_value=0,
                    value=active_vehicle.get('current_mileage', 0)
                )
                last_service_date = st.date_input(
                    "Last Service Date",
                    value=pd.to_datetime(active_vehicle.get('last_service_date', '2024-01-01'))
                )
            
            submitted = st.form_submit_button("💾 Save Vehicle Information")
            
            if submitted:
                vehicle_info = {
                    'registration_number': registration_number,
                    'manufacturer': manufacturer,
                    'model': model,
                    'manufacturing_year': manufacturing_year,
                    'fuel_type': fuel_type,
                    'transmission_type': transmission_type,
                    'current_mileage': current_mileage,
                    'last_service_date': str(last_service_date)
                }
                save_vehicle_data(vehicle_info)
    
    # ========================================================================
    # PAGE 3: DIAGNOSE VEHICLE
    # ========================================================================
    elif page == "🔍 Diagnose Vehicle":
        st.subheader("Vehicle Diagnosis")
        
        active_vehicle = db.get_vehicle(st.session_state.active_vehicle_reg) if st.session_state.active_vehicle_reg else None
        
        if not active_vehicle:
            st.error("❌ Please register a vehicle first before diagnosing.")
        else:
            st.write(f"**Vehicle**: {active_vehicle['manufacturer']} {active_vehicle['model']}")
            st.write(f"**Registration**: {active_vehicle['registration_number']}")
            
            # OBD & Voice Import Options
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Import Live OBD-II Data"):
                    live_data = obd.get_live_data(fault_mode="Random")
                    st.session_state.temp_obd_data = live_data
                    st.success("✅ Live data imported!")
            with col2:
                voice_input = st.text_input("🎤 Describe Problem (Voice Simulation)", placeholder="e.g. My car is vibrating and engine is hot")
                if voice_input:
                    voice_symptoms = extract_symptoms_from_text(voice_input)
                    if voice_symptoms:
                        st.session_state.voice_symptoms = voice_symptoms
                        st.success(f"✅ Detected: {', '.join(voice_symptoms)}")
            
            st.markdown("---")
            
            # Use imported data if available
            default_temp = 90
            default_rpm = 800
            default_voltage = 12.6
            default_dtc = "None"
            
            if 'temp_obd_data' in st.session_state:
                default_temp = st.session_state.temp_obd_data['Engine Temperature']
                default_rpm = st.session_state.temp_obd_data['RPM']
                default_voltage = st.session_state.temp_obd_data['Battery Voltage']
                default_dtc = st.session_state.temp_obd_data['DTC']
            
            st.write("**Select symptoms your vehicle is experiencing:**")
            
            st.write("**Select symptoms your vehicle is experiencing:**")
            
            # Symptom categories
            symptoms_dict = {
                "🔧 Engine": [
                    "Engine vibration",
                    "Engine overheating",
                    "Engine not starting",
                    "Engine stalling",
                    "Poor acceleration",
                    "Low engine power"
                ],
                "⛽ Fuel": [
                    "Poor mileage",
                    "High fuel consumption",
                    "Fuel smell"
                ],
                "🛑 Brakes": [
                    "Brake noise",
                    "Brake vibration",
                    "Weak braking"
                ],
                "⚡ Electrical": [
                    "Battery problem",
                    "Starter problem",
                    "Warning light"
                ],
                "🔊 Sound": [
                    "Clicking sound",
                    "Grinding sound",
                    "Knocking sound",
                    "Whistling sound"
                ]
            }
            
            selected_symptoms = []
            
            # Pre-select symptoms from voice if available
            voice_syms = st.session_state.get('voice_symptoms', [])
            
            for category, symptoms in symptoms_dict.items():
                with st.expander(category, expanded=False):
                    for symptom in symptoms:
                        is_checked = st.checkbox(symptom, key=f"symptom_{symptom}", value=(symptom in voice_syms))
                        if is_checked:
                            selected_symptoms.append(symptom)
            
            st.markdown("---")
            st.write("**Additional Sensor Data (Optional - For AI Model):**")
            col1, col2, col3 = st.columns(3)
            with col1:
                engine_temp = st.slider("Engine Temperature (°C)", 40, 130, default_temp)
                rpm = st.number_input("Engine RPM", 0, 8000, default_rpm)
            with col2:
                battery_voltage = st.slider("Battery Voltage (V)", 9.0, 15.0, default_voltage)
                mileage = st.number_input("Current Mileage (km)", 0, 500000, active_vehicle.get('current_mileage', 0))
            with col3:
                dtc_input = st.text_input("DTC Code (e.g. P0301)", value=default_dtc)
                vehicle_age = datetime.now().year - active_vehicle.get('manufacturing_year', 2020)
                st.write(f"Vehicle Age: {vehicle_age} years")
            
            # DTC Lookup Logic
            if dtc_input != "None" and dtc_input != "":
                dtc_info = obd.get_dtc_details(dtc_input)
                st.warning(f"⚠️ **DTC Detected: {dtc_input}** - {dtc_info['description']}")
                if st.checkbox("Apply DTC Symptoms to AI Model"):
                    if dtc_input.startswith("P03"): selected_symptoms.append("Engine vibration")
                    if dtc_input == "P0117": selected_symptoms.append("Engine overheating")
                    if dtc_input == "P0562": selected_symptoms.append("Battery problem")
            with col3:
                vehicle_age = datetime.now().year - active_vehicle.get('manufacturing_year', 2020)
                st.write(f"Vehicle Age: {vehicle_age} years")

            # Map UI symptoms to ML features
            symptom_map = {
                "Engine vibration": "engine_vibration",
                "Engine overheating": "engine_overheating",
                "Poor mileage": "poor_mileage",
                "Engine not starting": "starting_problem",
                "Warning light": "check_engine_light",
                "Brake noise": "brake_noise",
                "Battery problem": "battery_problem",
                "Low engine power": "low_power",
                "Clicking sound": "abnormal_sound"
            }

            diagnosis_mode = st.radio("Diagnosis Mode", ["AI Model (Random Forest)", "Rule-Based (Legacy)"], horizontal=True)

            if st.button("🔍 Diagnose Vehicle"):
                if not selected_symptoms and diagnosis_mode == "Rule-Based (Legacy)":
                    st.error("❌ Please select at least one symptom.")
                else:
                    if diagnosis_mode == "AI Model (Random Forest)":
                        # Prepare input for ML
                        input_data = {
                            'vehicle_age': vehicle_age,
                            'mileage': mileage,
                            'engine_temperature': engine_temp,
                            'rpm': rpm,
                            'battery_voltage': battery_voltage
                        }
                        # Add symptoms
                        for ui_sym, ml_feat in symptom_map.items():
                            input_data[ml_feat] = 1 if ui_sym in selected_symptoms else 0
                        
                        # Handle other symptoms not in map as noise/abnormal sound
                        if any(s in selected_symptoms for s in ["Grinding sound", "Knocking sound", "Whistling sound"]):
                            input_data['abnormal_sound'] = 1

                        diagnosis_result = predictor.predict(input_data)
                        diagnosis_result['symptoms'] = selected_symptoms
                    else:
                        # Perform rule-based diagnosis
                        diagnosis_result = rule_based_diagnosis(selected_symptoms)
                    
                    # Save to history
                    save_diagnosis_to_history(diagnosis_result)
                    
                    # Display results
                    st.markdown("---")
                    st.subheader("📊 Diagnosis Results")
                    
                    # Severity color coding
                    severity_colors = {
                        'LOW': '🟢',
                        'MEDIUM': '🟡',
                        'HIGH': '🟠',
                        'CRITICAL': '🔴'
                    }
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Predicted Fault", diagnosis_result['fault'])
                    with col2:
                        st.metric("Confidence", f"{diagnosis_result['confidence']}%")
                    with col3:
                        severity_icon = severity_colors.get(diagnosis_result['severity'], '❓')
                        st.metric("Severity", f"{severity_icon} {diagnosis_result['severity']}")
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🔍 Possible Causes")
                        for i, cause in enumerate(diagnosis_result['causes'], 1):
                            st.write(f"{i}. {cause}")
                    
                    with col2:
                        st.subheader("✅ Recommended Action")
                        st.info(diagnosis_result['recommendation'])
                    
                    st.markdown("---")
                    
                    # PDF Report Generation
                    report_filename = f"report_{active_vehicle['registration_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    reports_dir = PROJECT_ROOT / 'reports'
                    reports_dir.mkdir(parents=True, exist_ok=True)
                    report_path = reports_dir / report_filename
                    generate_pdf_report(active_vehicle, diagnosis_result, str(report_path))
                    
                    with open(report_path, "rb") as f:
                        st.download_button(
                            label="📄 Download Diagnosis Report (PDF)",
                            data=f,
                            file_name=report_filename,
                            mime="application/pdf"
                        )
                    
                    st.success("✅ Diagnosis saved to history!")
    
    # ========================================================================
    # PAGE 4: OBD-II MONITOR
    # ========================================================================
    elif page == "📡 OBD-II Monitor":
        st.subheader("Live OBD-II Monitor (Simulation)")
        
        active_vehicle = db.get_vehicle(st.session_state.active_vehicle_reg) if st.session_state.active_vehicle_reg else None
        
        if not active_vehicle:
            st.error("❌ Please register a vehicle first.")
        else:
            st.write(f"Monitoring: **{active_vehicle['manufacturer']} {active_vehicle['model']}**")
            
            # Simulation Controls
            col1, col2 = st.columns(2)
            with col1:
                sim_mode = st.selectbox("Simulation Mode", ["Normal", "Engine Misfire", "Cooling System Problem", "Battery Problem", "Random"])
            with col2:
                if st.button("🔄 Refresh Live Data"):
                    st.session_state.live_obd = obd.get_live_data(fault_mode=sim_mode)
            
            if 'live_obd' not in st.session_state:
                st.session_state.live_obd = obd.get_live_data(fault_mode="Normal")
            
            data = st.session_state.live_obd
            
            # Display Gauges/Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("RPM", f"{data['RPM']}")
            m2.metric("Temp", f"{data['Engine Temperature']}°C")
            m3.metric("Voltage", f"{data['Battery Voltage']}V")
            m4.metric("Speed", f"{data['Vehicle Speed']} km/h")
            
            st.markdown("---")
            
            # DTC Status
            if data['DTC'] == "None":
                st.success("✅ No Diagnostic Trouble Codes (DTC) detected.")
            else:
                st.error(f"🚨 Active DTC: {data['DTC']}")
                dtc_info = obd.get_dtc_details(data['DTC'])
                st.write(f"**Description**: {dtc_info['description']}")
                st.write(f"**Severity**: {dtc_info['severity']}")
                st.write(f"**Possible Causes**: {', '.join(dtc_info['causes'])}")
                
                if st.button("🛠️ Send to Diagnosis"):
                    st.session_state.temp_obd_data = data
                    st.info("Data sent! Go to 'Diagnose Vehicle' page to proceed.")

    # ========================================================================
    # PAGE 5: VEHICLE HEALTH
    # ========================================================================
    elif page == "📊 Vehicle Health":
        st.subheader("Vehicle Health Score")
        
        active_vehicle = db.get_vehicle(st.session_state.active_vehicle_reg) if st.session_state.active_vehicle_reg else None
        
        if not active_vehicle:
            st.error("❌ Please register a vehicle first.")
        else:
            history = db.get_diagnosis_history(st.session_state.active_vehicle_reg)
            last_severity = history.iloc[0]['severity'] if not history.empty else 'LOW'
            
            # Get latest OBD data for score
            obd_data = st.session_state.get('live_obd', obd.get_live_data())
            
            score, deductions = calculate_health_score(
                obd_data['DTC'],
                obd_data['Engine Temperature'],
                obd_data['Battery Voltage'],
                active_vehicle['current_mileage'],
                last_severity
            )
            
            # Display Score
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"<h1 style='text-align: center; color: {'green' if score > 80 else 'orange' if score > 50 else 'red'};'>{score}/100</h1>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center;'>Overall Health Score</p>", unsafe_allow_html=True)
            
            with col2:
                st.subheader("Health Analysis")
                if not deductions:
                    st.success("✅ Your vehicle is in excellent condition!")
                else:
                    for d in deductions:
                        st.write(f"• {d}")
            
            st.markdown("---")
            
            # Maintenance Reminders
            st.subheader("🔧 Maintenance Reminders")
            mileage = active_vehicle['current_mileage']
            
            reminders = []
            if mileage > 10000: reminders.append("🛢️ Oil Change recommended (every 10,000 km)")
            if mileage > 40000: reminders.append("🛑 Brake Pad Inspection recommended (every 40,000 km)")
            if mileage > 60000: reminders.append("🔋 Battery Health Check recommended (every 60,000 km)")
            
            if not reminders:
                st.info("No immediate maintenance required.")
            else:
                for r in reminders:
                    st.warning(r)

    # ========================================================================
    # PAGE 6: DIAGNOSIS HISTORY
    # ========================================================================
    elif page == "📋 Diagnosis History":
        st.subheader("Diagnosis History")
        
        history = db.get_diagnosis_history(st.session_state.active_vehicle_reg)
        
        if history.empty:
            st.info("📌 No diagnoses performed yet.")
        else:
            st.dataframe(history, use_container_width=True)
            
            st.markdown("---")
            st.write(f"**Total Diagnoses**: {len(history)}")

if __name__ == "__main__":
    main()

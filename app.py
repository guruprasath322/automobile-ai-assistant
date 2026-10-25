"""
AI Automobile Health & Diagnosis Assistant
FastAPI Web Application Server
Replaces Streamlit with a modern, high-performance web interface & REST API.
"""

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import os
import uvicorn
import pandas as pd

from ml.prediction import DiagnosisPredictor
from ml.dataset_analyzer import DatasetAnalyzer
from database.database import AutomobileDB
from obd.simulator import OBDSimulator
from voice.speech import extract_symptoms_from_text
from reports.report_generator import generate_pdf_report
from utils.helpers import calculate_health_score
from utils.maintenance import generate_maintenance_checklist

PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PROJECT_ROOT / "static"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Initialize core domain services
db = AutomobileDB()
predictor = DiagnosisPredictor()
obd = OBDSimulator()
dataset_analyzer = DatasetAnalyzer()

# In-memory active vehicle tracker
_active_vehicle_reg: Optional[str] = None

def get_active_vehicle_reg() -> Optional[str]:
    """Retrieve active vehicle reg or default to first registered vehicle."""
    global _active_vehicle_reg
    if _active_vehicle_reg:
        return _active_vehicle_reg
    all_v = db.get_all_vehicles()
    if not all_v.empty:
        _active_vehicle_reg = str(all_v.iloc[0]['registration_number'])
        return _active_vehicle_reg
    return None

def set_active_vehicle_reg(reg: str):
    global _active_vehicle_reg
    _active_vehicle_reg = reg


# ============================================================================
# RULE-BASED DIAGNOSIS ENGINE
# ============================================================================

def rule_based_diagnosis(selected_symptoms: List[str]) -> Dict[str, Any]:
    """
    Rule-based diagnosis system mapping symptom combinations to possible faults.
    """
    diagnosis_rules = {
        ('Engine vibration', 'Poor acceleration', 'Low engine power'): {
            'fault': 'Engine Misfire',
            'confidence': 85.0,
            'severity': 'HIGH',
            'causes': ['Spark plug issue', 'Ignition coil problem', 'Fuel injector malfunction'],
            'recommendation': 'Inspect ignition and fuel systems with a qualified technician.'
        },
        ('Engine vibration', 'Engine stalling'): {
            'fault': 'Fuel System Problem',
            'confidence': 75.0,
            'severity': 'MEDIUM',
            'causes': ['Fuel pump failure', 'Clogged fuel filter', 'Fuel pressure regulator issue'],
            'recommendation': 'Have the fuel system inspected and cleaned by a professional.'
        },
        ('Engine overheating',): {
            'fault': 'Cooling System Problem',
            'confidence': 80.0,
            'severity': 'HIGH',
            'causes': ['Low coolant level', 'Thermostat failure', 'Water pump issue'],
            'recommendation': 'Stop the vehicle immediately and allow it to cool. Check coolant level and consult a technician.'
        },
        ('Engine not starting',): {
            'fault': 'Starter Problem',
            'confidence': 70.0,
            'severity': 'HIGH',
            'causes': ['Battery discharge', 'Starter motor failure', 'Alternator issue'],
            'recommendation': 'Check battery voltage and connections. If problem persists, consult a technician.'
        },
        ('Brake noise', 'Brake vibration'): {
            'fault': 'Brake Pad Wear',
            'confidence': 88.0,
            'severity': 'MEDIUM',
            'causes': ['Brake pads worn out', 'Brake rotor damage', 'Brake fluid contamination'],
            'recommendation': 'Replace brake pads and inspect rotors. Do not delay this service.'
        },
        ('Weak braking',): {
            'fault': 'Brake System Problem',
            'confidence': 82.0,
            'severity': 'CRITICAL',
            'causes': ['Brake fluid leak', 'Air in brake lines', 'Master cylinder failure'],
            'recommendation': 'STOP driving immediately. Do not operate the vehicle. Seek professional help urgently.'
        },
        ('Battery problem', 'Warning light'): {
            'fault': 'Battery Problem',
            'confidence': 90.0,
            'severity': 'MEDIUM',
            'causes': ['Battery discharge', 'Alternator failure', 'Corroded terminals'],
            'recommendation': 'Check battery terminals for corrosion. Test battery voltage. Replace if needed.'
        },
        ('Starter problem', 'Clicking sound'): {
            'fault': 'Electrical System Problem',
            'confidence': 78.0,
            'severity': 'MEDIUM',
            'causes': ['Low battery', 'Starter relay issue', 'Corroded connections'],
            'recommendation': 'Inspect battery and electrical connections. Test starter motor.'
        },
        ('Poor mileage', 'High fuel consumption'): {
            'fault': 'Fuel System Problem',
            'confidence': 72.0,
            'severity': 'LOW',
            'causes': ['Faulty oxygen sensor', 'Clogged fuel injectors', 'Engine carbon buildup'],
            'recommendation': 'Clean fuel injectors and check oxygen sensor. Consider fuel system cleaning.'
        },
        ('Clicking sound',): {
            'fault': 'Electrical or Starter Problem',
            'confidence': 65.0,
            'severity': 'MEDIUM',
            'causes': ['Low battery', 'Starter motor issue', 'Bad connections'],
            'recommendation': 'Check battery voltage and connections first. Test starter if needed.'
        },
        ('Grinding sound',): {
            'fault': 'Brake or Transmission Problem',
            'confidence': 68.0,
            'severity': 'HIGH',
            'causes': ['Worn brake pads', 'Transmission issue', 'Differential problem'],
            'recommendation': 'Inspect brake system and transmission. Seek professional diagnosis.'
        },
        ('Knocking sound',): {
            'fault': 'Engine Knock / Detonation',
            'confidence': 70.0,
            'severity': 'MEDIUM',
            'causes': ['Low octane fuel', 'Carbon buildup', 'Ignition timing issue'],
            'recommendation': 'Use higher octane fuel. Have ignition timing checked by a technician.'
        },
        ('Whistling sound',): {
            'fault': 'Vacuum Leak or Belt Issue',
            'confidence': 62.0,
            'severity': 'LOW',
            'causes': ['Loose serpentine belt', 'Vacuum hose leak', 'Power steering pump issue'],
            'recommendation': 'Inspect belts and hoses. Tighten or replace as needed.'
        },
    }

    symptoms_tuple = tuple(sorted(selected_symptoms))
    if symptoms_tuple in diagnosis_rules:
        res = diagnosis_rules[symptoms_tuple].copy()
        res['symptoms'] = selected_symptoms
        return res

    best_match = None
    best_match_count = 0
    for rule_symptoms, rule_result in diagnosis_rules.items():
        matching_count = sum(1 for s in rule_symptoms if s in selected_symptoms)
        if matching_count > best_match_count:
            best_match = rule_result.copy()
            best_match_count = matching_count

    if best_match:
        best_match['symptoms'] = selected_symptoms
        return best_match

    return {
        'fault': 'Unable to determine specific fault',
        'confidence': 30.0,
        'severity': 'LOW',
        'causes': ['Insufficient symptom data', 'Rare combination of symptoms'],
        'recommendation': 'Consult a qualified mechanic for professional diagnosis.',
        'symptoms': selected_symptoms
    }


# ============================================================================
# FASTAPI APP & SCHEMAS
# ============================================================================

app = FastAPI(
    title="AI Automobile Health & Diagnosis Assistant",
    description="Intelligent automotive diagnostic API and web portal",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VehiclePayload(BaseModel):
    registration_number: str = Field(...)
    manufacturer: str = Field(...)
    model: str = Field(...)
    manufacturing_year: int = Field(..., ge=1990, le=2030)
    fuel_type: str = Field(...)
    transmission_type: str = Field(...)
    current_mileage: int = Field(..., ge=0)
    last_service_date: str = Field(...)


class ActiveVehiclePayload(BaseModel):
    registration_number: str


class DiagnosisPayload(BaseModel):
    vehicle_reg: Optional[str] = None
    mode: str = Field("ai", description="'ai' or 'rule'")
    symptoms: List[str] = Field(default_factory=list)
    engine_temp: float = 90.0
    rpm: int = 800
    battery_voltage: float = 12.6
    mileage: Optional[int] = None
    dtc_code: Optional[str] = "None"


class VoiceExtractPayload(BaseModel):
    text: str


# ============================================================================
# STATIC FILES & ROOT ROUTE
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(
        content="<h1>AI Automobile Health Assistant</h1><p>Frontend file static/index.html is loading...</p>"
    )


# ============================================================================
# VEHICLE API ROUTES
# ============================================================================

@app.get("/api/vehicles")
def list_vehicles():
    """Retrieve all registered vehicles."""
    df = db.get_all_vehicles()
    return {"vehicles": df.to_dict(orient="records")}


@app.get("/api/vehicles/{registration_number}")
def get_vehicle_by_reg(registration_number: str):
    """Retrieve details for a single vehicle."""
    vehicle = db.get_vehicle(registration_number)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"vehicle": vehicle}


@app.post("/api/vehicles")
def save_vehicle(payload: VehiclePayload):
    """Register or update a vehicle."""
    data = payload.model_dump()
    db.save_vehicle(data)
    set_active_vehicle_reg(data["registration_number"])
    return {
        "success": True,
        "message": f"Vehicle {data['registration_number']} saved successfully.",
        "vehicle": data
    }


@app.delete("/api/vehicles/{registration_number}")
def delete_vehicle(registration_number: str):
    """Remove a vehicle and its history."""
    db.delete_vehicle(registration_number)
    global _active_vehicle_reg
    if _active_vehicle_reg == registration_number:
        _active_vehicle_reg = None
        get_active_vehicle_reg()
    return {"success": True, "message": f"Vehicle {registration_number} deleted."}


@app.get("/api/active-vehicle")
def get_active_vehicle():
    """Get currently active vehicle details."""
    reg = get_active_vehicle_reg()
    if not reg:
        return {"vehicle": None}
    vehicle = db.get_vehicle(reg)
    return {"vehicle": vehicle}


@app.post("/api/active-vehicle")
def set_active_vehicle(payload: ActiveVehiclePayload):
    """Set active vehicle."""
    vehicle = db.get_vehicle(payload.registration_number)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    set_active_vehicle_reg(payload.registration_number)
    return {"success": True, "active_vehicle": vehicle}


# ============================================================================
# OBD-II TELEMETRY & DTC LOOKUP ROUTES
# ============================================================================

@app.get("/api/obd/live")
def get_live_obd(fault_mode: Optional[str] = Query(None, description="Fault mode to simulate")):
    """Simulate live OBD-II vehicle telemetry."""
    mode = fault_mode if fault_mode in [
        "Normal", "Engine Misfire", "Cooling System Problem", "Battery Problem", "Random"
    ] else "Normal"
    data = obd.get_live_data(fault_mode=mode)
    
    dtc_info = None
    if data.get("DTC") and data["DTC"] != "None":
        dtc_info = obd.get_dtc_details(data["DTC"])
        
    return {
        "telemetry": data,
        "dtc_info": dtc_info,
        "mode": mode,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@app.get("/api/obd/dtc/{code}")
def get_dtc_details(code: str):
    """Lookup diagnostic trouble code details."""
    details = obd.get_dtc_details(code)
    return {"dtc": code, "details": details}


# ============================================================================
# VOICE & SYMPTOM NLP ROUTE
# ============================================================================

@app.post("/api/voice/extract")
def extract_symptoms(payload: VoiceExtractPayload):
    """Extract recognized vehicle symptoms from spoken or typed natural language."""
    symptoms = extract_symptoms_from_text(payload.text)
    return {"text": payload.text, "symptoms": symptoms}


# ============================================================================
# DIAGNOSIS ENGINE & REPORT ROUTES
# ============================================================================

@app.post("/api/diagnose")
def diagnose_vehicle(payload: DiagnosisPayload):
    """
    Perform vehicle diagnosis using AI Machine Learning (Random Forest)
    or Rule-Based Engine, save the record, and generate a PDF report.
    """
    reg = payload.vehicle_reg or get_active_vehicle_reg()
    vehicle = db.get_vehicle(reg) if reg else None
    
    if not vehicle:
        raise HTTPException(
            status_code=400,
            detail="No vehicle registered. Please register a vehicle before diagnosing."
        )

    selected_symptoms = list(payload.symptoms)

    # Automatically add symptoms associated with DTC code if provided
    dtc = (payload.dtc_code or "").strip()
    if dtc and dtc != "None":
        if dtc.startswith("P03") and "Engine vibration" not in selected_symptoms:
            selected_symptoms.append("Engine vibration")
        if dtc == "P0117" and "Engine overheating" not in selected_symptoms:
            selected_symptoms.append("Engine overheating")
        if dtc == "P0562" and "Battery problem" not in selected_symptoms:
            selected_symptoms.append("Battery problem")

    vehicle_age = max(0, datetime.now().year - vehicle.get("manufacturing_year", 2020))
    mileage = payload.mileage if payload.mileage is not None else vehicle.get("current_mileage", 40000)

    # Symptom mapping to ML features
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

    input_data = {
        'vehicle_age': vehicle_age,
        'mileage': mileage,
        'engine_temperature': payload.engine_temp,
        'rpm': payload.rpm,
        'battery_voltage': payload.battery_voltage
    }
    for ui_sym, ml_feat in symptom_map.items():
        input_data[ml_feat] = 1 if ui_sym in selected_symptoms else 0

    if any(s in selected_symptoms for s in ["Grinding sound", "Knocking sound", "Whistling sound"]):
        input_data['abnormal_sound'] = 1

    if payload.mode == "ai":
        diagnosis_result = predictor.predict(input_data)
        if not diagnosis_result:
            # Fallback to rule engine if ML model failed
            diagnosis_result = rule_based_diagnosis(selected_symptoms)
        else:
            diagnosis_result['symptoms'] = selected_symptoms
    else:
        diagnosis_result = rule_based_diagnosis(selected_symptoms)

    # Attach deep dataset evidence & verification details
    try:
        dataset_evidence = dataset_analyzer.generate_diagnostic_evidence(
            diagnosis_result['fault'],
            input_data,
            selected_symptoms
        )
        diagnosis_result['dataset_evidence'] = dataset_evidence
    except Exception as e:
        print(f"Error computing dataset evidence: {e}")
        diagnosis_result['dataset_evidence'] = None

    # Persist in SQLite database
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    diagnosis_record = {
        'timestamp': now_str,
        'vehicle': vehicle['registration_number'],
        'symptoms': selected_symptoms,
        'predicted_fault': diagnosis_result['fault'],
        'confidence': diagnosis_result['confidence'],
        'severity': diagnosis_result['severity'],
        'recommendation': diagnosis_result['recommendation']
    }
    db.save_diagnosis(diagnosis_record)

    # Generate PDF Report
    safe_reg = vehicle['registration_number'].replace(" ", "_").replace("-", "_")
    report_filename = f"report_{safe_reg}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    report_path = REPORTS_DIR / report_filename
    try:
        generate_pdf_report(vehicle, diagnosis_result, str(report_path))
        has_report = True
    except Exception as e:
        print(f"PDF generation error: {e}")
        has_report = False

    return {
        "success": True,
        "diagnosis": diagnosis_result,
        "vehicle": vehicle,
        "report_filename": report_filename if has_report else None,
        "report_url": f"/api/reports/download/{report_filename}" if has_report else None,
        "timestamp": now_str
    }


# ============================================================================
# DATASET & FAULT KNOWLEDGE REPOSITORY ROUTES
# ============================================================================

@app.get("/api/dataset/overview")
def get_dataset_overview():
    """Retrieve statistical overview and fault class distributions from dataset.csv."""
    return dataset_analyzer.get_dataset_overview()


@app.get("/api/dataset/faults")
def get_dataset_faults_catalog():
    """Retrieve full catalog of all 8 fault classes with metrics and repair guides."""
    return {"faults": dataset_analyzer.get_all_faults_catalog()}


@app.get("/api/dataset/fault/{fault_name}")
def get_fault_detail(fault_name: str):
    """Retrieve comprehensive details, DTC codes, and sensor benchmarks for a fault."""
    detail = dataset_analyzer.get_fault_detail(fault_name)
    if not detail:
        raise HTTPException(status_code=404, detail="Fault not found in dataset knowledge base")
    return {"fault_detail": detail}


@app.get("/api/dataset/records")
def get_dataset_records(
    fault: Optional[str] = Query(None, description="Optional fault filter"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Paginated retrieval of raw historical records from data/dataset.csv."""
    return dataset_analyzer.query_dataset_records(fault=fault, limit=limit, offset=offset)


@app.get("/api/reports/download/{filename}")
def download_pdf_report(filename: str):
    """Download a generated PDF diagnosis report."""
    safe_name = os.path.basename(filename)
    file_path = REPORTS_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(
        path=str(file_path),
        filename=safe_name,
        media_type="application/pdf"
    )


# ============================================================================
# VEHICLE HEALTH SCORE & HISTORY ROUTES
# ============================================================================

@app.get("/api/health-score")
def get_vehicle_health_score(vehicle_reg: Optional[str] = None):
    """Calculate health score and maintenance advice for the specified or active vehicle."""
    reg = vehicle_reg or get_active_vehicle_reg()
    if not reg:
        return {"score": 100, "deductions": [], "reminders": [], "status": "No active vehicle"}

    vehicle = db.get_vehicle(reg)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    history = db.get_diagnosis_history(reg)
    last_severity = history.iloc[0]['severity'] if not history.empty else 'LOW'

    # Sample live OBD readings
    telemetry = obd.get_live_data(fault_mode="Normal")

    score, deductions = calculate_health_score(
        telemetry['DTC'],
        telemetry['Engine Temperature'],
        telemetry['Battery Voltage'],
        vehicle.get('current_mileage', 0),
        last_severity
    )

    mileage = vehicle.get('current_mileage', 0)
    reminders = []
    if mileage > 10000:
        reminders.append({"service": "Engine Oil & Filter Change", "interval": "Every 10,000 km", "status": "Due"})
    if mileage > 40000:
        reminders.append({"service": "Brake Pad & Rotor Inspection", "interval": "Every 40,000 km", "status": "Due"})
    if mileage > 60000:
        reminders.append({"service": "Battery & Alternator Diagnostic", "interval": "Every 60,000 km", "status": "Recommended"})
    if mileage > 80000:
        reminders.append({"service": "Spark Plugs & Transmission Fluid Flush", "interval": "Every 80,000 km", "status": "Recommended"})

    return {
        "vehicle": vehicle,
        "score": score,
        "deductions": deductions,
        "reminders": reminders,
        "last_severity": last_severity,
        "telemetry_used": telemetry
    }


@app.get("/api/maintenance/checklist")
def get_maintenance_checklist(vehicle_reg: Optional[str] = None):
    """Return maintenance actions for the specified or active vehicle."""
    reg = vehicle_reg or get_active_vehicle_reg()
    if not reg:
        return {"vehicle": None, "checklist": []}

    vehicle = db.get_vehicle(reg)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    telemetry = obd.get_live_data(fault_mode="Normal")
    checklist = generate_maintenance_checklist(
        mileage=vehicle.get("current_mileage", 0),
        engine_temp=telemetry["Engine Temperature"],
        battery_voltage=telemetry["Battery Voltage"],
        last_service_date=vehicle.get("last_service_date"),
    )
    return {
        "vehicle": vehicle,
        "checklist": checklist,
        "telemetry_used": telemetry,
    }


@app.get("/api/history")
def get_history(vehicle_reg: Optional[str] = None):
    """Retrieve diagnosis history records."""
    reg = vehicle_reg or get_active_vehicle_reg()
    df = db.get_diagnosis_history(reg)
    records = df.to_dict(orient="records")
    return {"history": records, "vehicle_reg": reg, "total": len(records)}


@app.get("/api/stats")
def get_dashboard_stats():
    """Aggregate high-level dashboard metrics."""
    vehicles_df = db.get_all_vehicles()
    active_reg = get_active_vehicle_reg()
    active_vehicle = db.get_vehicle(active_reg) if active_reg else None
    
    history_df = db.get_diagnosis_history()
    active_history = db.get_diagnosis_history(active_reg) if active_reg else pd.DataFrame()

    last_diag = active_history.iloc[0].to_dict() if not active_history.empty else None

    # Calculate quick score
    score = 100
    if active_vehicle:
        last_sev = last_diag['severity'] if last_diag else 'LOW'
        score, _ = calculate_health_score(
            "None", 90, 12.6, active_vehicle.get('current_mileage', 0), last_sev
        )

    return {
        "total_vehicles": len(vehicles_df),
        "active_vehicle": active_vehicle,
        "total_diagnoses": len(history_df),
        "active_vehicle_diagnoses": len(active_history),
        "last_diagnosis": last_diag,
        "health_score": score
    }


# Mount static assets after defining API routes
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

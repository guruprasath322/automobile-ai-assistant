"""
Dataset Analyzer & Knowledge Engine for Automobile Fault Diagnosis
Analyzes the 1,500+ records in data/dataset.csv and cross-references DTC codes.
Provides deep diagnostic evidence, similarity matching, sensor benchmarking,
and comprehensive fault cataloging.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "dataset.csv"
DTC_PATH = PROJECT_ROOT / "data" / "dtc_codes.csv"


class DatasetAnalyzer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatasetAnalyzer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return

        self.dataset_df = pd.read_csv(DATASET_PATH)
        self.dtc_df = pd.read_csv(DTC_PATH) if DTC_PATH.exists() else pd.DataFrame()
        self._build_fault_knowledge_base()
        self._compute_dataset_distributions()
        self._initialized = True

    def _build_fault_knowledge_base(self):
        """Construct deep domain knowledge for all diagnostic categories in the dataset."""
        self.fault_knowledge = {
            'Engine Misfire': {
                'fault': 'Engine Misfire',
                'category': 'Powertrain & Combustion',
                'severity': 'HIGH',
                'summary': 'Incomplete or absent combustion cycle in one or more cylinders. Fuel mixture fails to ignite cleanly, causing rotational imbalance, loss of power, and high emissions.',
                'causes': [
                    'Spark plug electrode gap wear or severe carbon fouling',
                    'Ignition coil insulation breakdown or primary circuit failure',
                    'Clogged or leaking electronic fuel injector nozzle',
                    'Low compression due to leaking valves or worn piston rings'
                ],
                'affected_components': [
                    {'name': 'Spark Plugs', 'role': 'High-voltage spark ignition', 'status': 'Critical Inspection', 'wear': 'Electrode erosion / Carbon fouling'},
                    {'name': 'Ignition Coils', 'role': 'Step-up voltage generator (30kV)', 'status': 'High Risk', 'wear': 'Secondary winding degradation'},
                    {'name': 'Fuel Injectors', 'role': 'Pressurized fuel atomization', 'status': 'Inspection Needed', 'wear': 'Varnish deposits / Solenoid failure'},
                    {'name': 'Catalytic Converter', 'role': 'Exhaust emissions scrub', 'status': 'At Risk of Melting', 'wear': 'Unburned fuel thermal shock'}
                ],
                'danger_level': 'High Hazard: Driving with active misfires sends raw fuel into the catalytic converter, exceeding 1,000°C and causing honeycomb melting and fire risk.',
                'workshop_procedure': [
                    'Connect OBD-II scanner and read cylinder-specific freeze frame data (P0300-P0304)',
                    'Measure primary and secondary coil winding resistance with a digital multimeter',
                    'Remove and inspect spark plugs for color, gap width (spec 0.8-1.1mm), and wet fuel',
                    'Execute fuel injector pulse test and cylinder balance compression test'
                ],
                'estimated_repair_time': '1.5 – 3.0 Hours',
                'repair_difficulty': 'Moderate',
                'dtc_codes': ['P0300', 'P0301'],
                'recommendation': 'Avoid high engine speeds or heavy towing immediately. Inspect ignition coils and replace fouled spark plugs with OEM heat-range units.'
            },
            'Cooling System Problem': {
                'fault': 'Cooling System Problem',
                'category': 'Thermal Management & Cooling',
                'severity': 'HIGH',
                'summary': 'Engine coolant loop failure leading to elevated cylinder head temperatures. Inability to dissipate engine thermal load can cause head gasket blowout and warped engine blocks.',
                'causes': [
                    'Stuck closed thermostat preventing radiator circulation',
                    'Coolant fluid loss due to hose split, radiator puncture, or heater core leak',
                    'Impeller failure or slippage in engine water pump',
                    'Electric radiator cooling fan motor or relay failure'
                ],
                'affected_components': [
                    {'name': 'Engine Thermostat', 'role': 'Thermal regulation valve (82-92°C)', 'status': 'High Risk', 'wear': 'Wax pellet mechanical lockup'},
                    {'name': 'Water Pump', 'role': 'Coolant coolant circulation', 'status': 'Inspect Impeller', 'wear': 'Bearing play / Impeller corrosion'},
                    {'name': 'Radiator & Hoses', 'role': 'Air-to-liquid heat exchange', 'status': 'Check Leaks', 'wear': 'Fin clogging / Hose embrittlement'},
                    {'name': 'Cylinder Head Gasket', 'role': 'High-pressure block sealing', 'status': 'Critical Risk', 'wear': 'Thermal distortion breach'}
                ],
                'danger_level': 'Extreme Hazard: Operating temperature above 115°C will warp aluminum cylinder heads within minutes, resulting in multi-thousand dollar engine rebuild costs.',
                'workshop_procedure': [
                    'Safely wait until engine is completely cold (minimum 45 minutes) before inspecting expansion tank',
                    'Perform cooling system pressure test at 15 PSI to locate external and internal leaks',
                    'Check thermostat opening temperature using infrared thermometer on upper radiator hose',
                    'Verify electric radiator cooling fan engages when temperature exceeds 96°C'
                ],
                'estimated_repair_time': '2.0 – 4.0 Hours',
                'repair_difficulty': 'Moderate to Advanced',
                'dtc_codes': ['P0117'],
                'recommendation': 'STOP driving immediately if temperature gauge exceeds normal. Check expansion tank level when cold and replace faulty thermostat or pump.'
            },
            'Battery Problem': {
                'fault': 'Battery Problem',
                'category': 'Electrical & Energy Storage',
                'severity': 'MEDIUM',
                'summary': 'Degraded state-of-charge or internal cell failure in 12V lead-acid / AGM battery. Inadequate terminal voltage impairs ECU bootup, starter cranking, and sensor calibration.',
                'causes': [
                    'Battery plate sulfation due to deep discharge or age (>3-4 years)',
                    'Failing alternator diode bridge or loose serpentine alternator belt',
                    'Parasitic battery draw from interior lighting or aftermarket accessories',
                    'High electrical contact resistance from oxidized, corroded terminal posts'
                ],
                'affected_components': [
                    {'name': '12V Starter Battery', 'role': 'Chemical electrical reservoir', 'status': 'Test Cranking Amps', 'wear': 'Lead sulfate plate buildup'},
                    {'name': 'Alternator & Regulator', 'role': 'Charging generation (13.8 - 14.5V)', 'status': 'Inspect Diodes', 'wear': 'Brush wear / Diode ripple'},
                    {'name': 'Battery Terminal Terminals', 'role': 'Heavy gauge copper connections', 'status': 'Clean & Tighten', 'wear': 'White lead sulfate oxidation'},
                    {'name': 'Starter Solenoid Relay', 'role': 'High current ignition relay', 'status': 'Check Voltage Drop', 'wear': 'Pitted internal contacts'}
                ],
                'danger_level': 'Stranded Vehicle Risk: Terminal voltage below 11.5V prevents starter engagement and may cause sudden sensor miscalculations while driving.',
                'workshop_procedure': [
                    'Perform open-circuit resting voltage test (Healthy: 12.6V, Discharged: <12.0V)',
                    'Execute cold cranking amp (CCA) conductance test with digital battery analyzer',
                    'Test alternator charging voltage under full electrical load (headlights + AC on)',
                    'Inspect and wire-brush terminal clamps, applying dielectric corrosion inhibitor grease'
                ],
                'estimated_repair_time': '30 – 60 Minutes',
                'repair_difficulty': 'Simple',
                'dtc_codes': ['P0562'],
                'recommendation': 'Clean terminal posts with baking soda solution. Test resting voltage and alternator charging output. Replace battery if older than 3 years.'
            },
            'Starter Problem': {
                'fault': 'Starter Problem',
                'category': 'Starting & Electrical Actuation',
                'severity': 'HIGH',
                'summary': 'Mechanical or electromechanical failure in the starter motor assembly. The pinion gear fails to mesh with the flywheel ring gear or the armature motor draws excessive locked-rotor current.',
                'causes': [
                    'Worn internal starter motor carbon brushes or pitted commutator segments',
                    'Burnt starter solenoid contact disc causing single or rapid clicking sounds',
                    'Damaged pinion overrunning clutch (bendix gear slipping)',
                    'Corroded heavy engine ground strap causing severe voltage drop during crank'
                ],
                'affected_components': [
                    {'name': 'Starter Motor Armature', 'role': 'Rotational high-torque cranking', 'status': 'Check Brushes', 'wear': 'Worn carbon brushes / Open windings'},
                    {'name': 'Starter Solenoid', 'role': 'Gear engagement & electrical contact', 'status': 'Test Activation', 'wear': 'Burned contact copper studs'},
                    {'name': 'Engine Flywheel Ring Gear', 'role': 'Crankshaft gear interface', 'status': 'Visual Inspection', 'wear': 'Stripped or chipped gear teeth'},
                    {'name': 'Chassis Ground Strap', 'role': 'High-amperage return loop', 'status': 'Check Continuity', 'wear': 'Oxidation / Frayed copper braid'}
                ],
                'danger_level': 'No-Start Immobilization: The vehicle cannot be cranked or started without jumpstart or push starting (manual transmissions only).',
                'workshop_procedure': [
                    'Verify 12V signal arrives at starter solenoid terminal 50 during key-turn',
                    'Perform cranking voltage drop test between battery negative and engine block',
                    'Bench test starter motor for free-spin amperage and pinion extension',
                    'Inspect flywheel teeth through inspection portal for mechanical damage'
                ],
                'estimated_repair_time': '1.5 – 3.0 Hours',
                'repair_difficulty': 'Moderate',
                'dtc_codes': ['P0562', 'P0507'],
                'recommendation': 'Inspect wiring harness from ignition switch to starter solenoid. Bench test starter motor and replace worn starter assembly.'
            },
            'Brake Pad Wear': {
                'fault': 'Brake Pad Wear',
                'category': 'Braking & Kinetic Deceleration',
                'severity': 'MEDIUM',
                'summary': 'Friction material thickness on brake pads has eroded below the 3mm safe operating threshold. Metal wear indicators contact the rotor face, generating grinding and squealing.',
                'causes': [
                    'Normal abrasive kinetic wear from extended urban stop-and-go driving',
                    'Seized caliper guide slide pins causing uneven pad tapering and drag',
                    'Scored or heat-glazed brake disc rotors reducing friction coefficient',
                    'Low or moisture-contaminated DOT3/DOT4 brake fluid in hydraulic lines'
                ],
                'affected_components': [
                    {'name': 'Front/Rear Brake Pads', 'role': 'Abrasive kinetic friction stopping', 'status': 'Replace Urgently', 'wear': 'Friction lining < 3mm thickness'},
                    {'name': 'Brake Rotors (Discs)', 'role': 'Cast iron heat dissipation surface', 'status': 'Measure Thickness', 'wear': 'Grooves / Thermal runout warpage'},
                    {'name': 'Caliper Slide Pins', 'role': 'Floating caliper alignment', 'status': 'Lubricate', 'wear': 'Hardened grease / Corrosion seizure'},
                    {'name': 'Hydraulic Fluid Lines', 'role': 'Incompressible pressure transfer', 'status': 'Inspect Fluid', 'wear': 'Moisture contamination (>2% water)'}
                ],
                'danger_level': 'Safety Critical: Extended stopping distances and rotor gouging. Metal-on-metal braking increases stopping distance by up to 40% and risks brake fade.',
                'workshop_procedure': [
                    'Remove road wheels and measure brake pad thickness using precision vernier caliper',
                    'Inspect rotor face for deep score lines, heat discoloration, and lip edge ridge',
                    'Test caliper piston retraction and clean guide slide pins with high-temp silicone grease',
                    'Torque wheel lug nuts in star pattern to manufacturer specification (e.g. 110-120 Nm)'
                ],
                'estimated_repair_time': '1.0 – 2.0 Hours',
                'repair_difficulty': 'Moderate',
                'dtc_codes': [],
                'recommendation': 'Replace brake pads as an axle set immediately. Inspect rotor disc thickness against discard minimum stamped on rotor hat.'
            },
            'Fuel System Problem': {
                'fault': 'Fuel System Problem',
                'category': 'Fuel Delivery & Metering',
                'severity': 'MEDIUM',
                'summary': 'Restricted fuel rail delivery, inadequate fuel pump discharge pressure, or contaminated injectors causing lean air-fuel stoichiometry (lambda > 1.05) and sluggish engine response.',
                'causes': [
                    'Clogged in-tank fuel strainer or inline fuel filter restricting flow',
                    'Electric fuel pump motor brush wear reducing rail pressure below OEM spec',
                    'Faulty fuel pressure regulator venting fuel back to tank prematurely',
                    'Clogged injector spray nozzles causing poor fuel droplets atomization'
                ],
                'affected_components': [
                    {'name': 'Electric Fuel Pump', 'role': 'High-pressure tank fuel lift (40-60 PSI)', 'status': 'Test Flow Pressure', 'wear': 'Brush wear / Filter sock clogging'},
                    {'name': 'Fuel Filter', 'role': 'Particulate trap (10 micron)', 'status': 'Replace Element', 'wear': 'Sediment accumulation / Flow restriction'},
                    {'name': 'Pressure Regulator', 'role': 'Constant fuel rail manifold delta', 'status': 'Check Diaphragm', 'wear': 'Leaking internal diaphragm'},
                    {'name': 'Fuel Injectors', 'role': 'Multi-hole solenoid atomization', 'status': 'Ultrasonic Cleaning', 'wear': 'Gum & varnish nozzle deposits'}
                ],
                'danger_level': 'Driveability Risk: High fuel consumption, severe hesitation when overtaking, engine stalling in traffic, and lean combustion overheating valves.',
                'workshop_procedure': [
                    'Hook up mechanical fuel pressure gauge to Schrader test port on fuel rail',
                    'Measure resting, key-on, and engine running fuel rail pressures',
                    'Perform fuel volume delivery test (Spec typically 1 liter per 30 seconds)',
                    'Inspect long-term fuel trim (LTFT) on live OBD-II scan tool (Healthy: -5% to +5%)'
                ],
                'estimated_repair_time': '1.5 – 3.5 Hours',
                'repair_difficulty': 'Moderate',
                'dtc_codes': ['P0171'],
                'recommendation': 'Replace fuel filter if overdue. Test fuel pump delivery pressure and run a professional fuel system cleaner through the induction rail.'
            },
            'Sensor Problem': {
                'fault': 'Sensor Problem',
                'category': 'Engine Management Sensors & Telemetry',
                'severity': 'LOW',
                'summary': 'Plausibility fault or open/short circuit in powertrain sensor bus (MAF, O2, MAP, or Coolant temp). The engine control unit (ECU) falls back to default open-loop limp-home tables.',
                'causes': [
                    'Dirty or oil-contaminated heated platinum wire in Mass Air Flow (MAF) sensor',
                    'Exhaust soot coated heated Oxygen (O2) sensor unable to switch lambda voltage',
                    'Loose, cracked, or corroded electrical connector pins on sensor harness',
                    'Intake vacuum air leak between MAF and throttle body skewing readings'
                ],
                'affected_components': [
                    {'name': 'Mass Air Flow Sensor', 'role': 'Inlet air mass measurement (g/s)', 'status': 'Clean Wire', 'wear': 'Dust / Oil film coating on platinum element'},
                    {'name': 'Upstream Oxygen Sensor', 'role': 'Exhaust stoichiometry lambda sensing', 'status': 'Inspect Waveform', 'wear': 'Silicone / Lead poisoning or aging'},
                    {'name': 'Coolant Temp Sensor (ECT)', 'role': 'Engine thermal state signal to ECU', 'status': 'Test Resistance', 'wear': 'Thermistor drift / Scale buildup'},
                    {'name': 'Wiring Harness / Plugs', 'role': '5V reference and ground path', 'status': 'Pin Tension Check', 'wear': 'Frayed wires / Corroded terminals'}
                ],
                'danger_level': 'Low Immediate Hazard: Vehicle will operate in open-loop failsafe mode with degraded fuel economy and increased exhaust emissions.',
                'workshop_procedure': [
                    'Connect diagnostic scanner and monitor sensor live PID graph data',
                    'Clean MAF hot wire element using specialized residue-free MAF cleaner spray',
                    'Measure 5V reference supply and sensor chassis ground resistance',
                    'Perform smoke machine test on intake tract to rule out vacuum leaks'
                ],
                'estimated_repair_time': '45 – 90 Minutes',
                'repair_difficulty': 'Simple to Moderate',
                'dtc_codes': ['P0101', 'P0420'],
                'recommendation': 'Scan specific sensor trouble codes. Clean Mass Air Flow sensor with electronics cleaner and check intake duct boots for unmetered air leaks.'
            },
            'Normal': {
                'fault': 'Normal',
                'category': 'Nominal Vehicle Health',
                'severity': 'LOW',
                'summary': 'All powertrain telemetry sensors, electrical potentials, thermal readings, and engine speed parameters operate cleanly within manufacturer baseline tolerances.',
                'causes': ['Vehicle in excellent mechanical and electrical health'],
                'affected_components': [
                    {'name': 'Engine Mechanicals', 'role': 'Compression & reciprocating power', 'status': 'Optimal (100%)', 'wear': 'Normal nominal clearances'},
                    {'name': 'Cooling System', 'role': 'Regulated 90°C thermal balance', 'status': 'Optimal (100%)', 'wear': 'Coolant clean, nominal level'},
                    {'name': 'Electrical Bus', 'role': '12.6V resting / 14.2V charging', 'status': 'Optimal (100%)', 'wear': 'Alternator output steady'},
                    {'name': 'Braking Hardware', 'role': 'Nominal friction and rotor thickness', 'status': 'Optimal (100%)', 'wear': 'Pads above safe minimum'}
                ],
                'danger_level': 'Zero Hazard: Vehicle is roadworthy and performing at optimal operational safety standards.',
                'workshop_procedure': [
                    'Continue scheduled preventive maintenance routines',
                    'Check engine oil and windshield washer levels periodically',
                    'Inspect tire inflation pressures including spare tire',
                    'Maintain vehicle service logbook for resale value retention'
                ],
                'estimated_repair_time': 'Routine Checkup: 15 Minutes',
                'repair_difficulty': 'None Required',
                'dtc_codes': [],
                'recommendation': 'All systems nominal. Continue following scheduled oil change and inspection intervals.'
            }
        }

    def _compute_dataset_distributions(self):
        """Pre-compute mathematical means, standard deviations, and symptom frequencies from the dataset."""
        df = self.dataset_df
        self.fault_counts = df['fault'].value_counts().to_dict()
        self.total_records = len(df)

        symptom_cols = [
            'engine_vibration', 'engine_overheating', 'poor_mileage',
            'starting_problem', 'check_engine_light', 'brake_noise',
            'battery_problem', 'low_power', 'abnormal_sound'
        ]
        num_cols = ['engine_temperature', 'rpm', 'battery_voltage', 'mileage', 'vehicle_age']

        # Means by fault
        self.fault_means = df.groupby('fault')[num_cols].mean().to_dict(orient='index')
        self.fault_symptoms = df.groupby('fault')[symptom_cols].mean().to_dict(orient='index')

        # Overall normal baseline
        normal_df = df[df['fault'] == 'Normal']
        self.normal_baseline = {
            'engine_temperature': round(float(normal_df['engine_temperature'].mean()), 1),
            'battery_voltage': round(float(normal_df['battery_voltage'].mean()), 2),
            'rpm': int(normal_df['rpm'].mean()),
            'mileage': int(normal_df['mileage'].mean()),
            'vehicle_age': round(float(normal_df['vehicle_age'].mean()), 1)
        }

        # Min / Max per sensor across dataset for normalization
        self.sensor_ranges = {}
        for c in num_cols:
            self.sensor_ranges[c] = {
                'min': float(df[c].min()),
                'max': float(df[c].max()),
                'mean': float(df[c].mean()),
                'std': float(df[c].std()) if df[c].std() > 0 else 1.0
            }

    def get_dataset_overview(self) -> Dict[str, Any]:
        """Return dataset statistics, sample counts, and distributions."""
        fault_distribution = []
        for fault, count in self.fault_counts.items():
            pct = round((count / self.total_records) * 100, 1)
            info = self.fault_knowledge.get(fault, {})
            means = self.fault_means.get(fault, {})
            fault_distribution.append({
                'fault': fault,
                'count': count,
                'percentage': pct,
                'severity': info.get('severity', 'LOW'),
                'category': info.get('category', 'Automotive System'),
                'avg_temp': round(means.get('engine_temperature', 90.0), 1),
                'avg_voltage': round(means.get('battery_voltage', 12.6), 2),
                'avg_rpm': int(means.get('rpm', 800)),
                'avg_mileage': int(means.get('mileage', 100000))
            })

        return {
            'total_records': self.total_records,
            'features_count': len(self.dataset_df.columns) - 1,
            'fault_classes_count': len(self.fault_counts),
            'normal_baseline': self.normal_baseline,
            'fault_distribution': fault_distribution
        }

    def get_all_faults_catalog(self) -> List[Dict[str, Any]]:
        """Return all 8 faults with their full technical details, dataset samples, and metrics."""
        catalog = []
        for fault_name, info in self.fault_knowledge.items():
            count = self.fault_counts.get(fault_name, 0)
            pct = round((count / self.total_records) * 100, 1) if self.total_records else 0
            means = self.fault_means.get(fault_name, {})
            symptoms_means = self.fault_symptoms.get(fault_name, {})

            # Filter high frequency symptoms in this fault
            top_symptoms = [
                s.replace('_', ' ').title()
                for s, prob in symptoms_means.items() if prob >= 0.3
            ]

            catalog.append({
                **info,
                'dataset_count': count,
                'dataset_percentage': pct,
                'sensor_means': {
                    'engine_temperature': round(means.get('engine_temperature', 90.0), 1),
                    'battery_voltage': round(means.get('battery_voltage', 12.6), 2),
                    'rpm': int(means.get('rpm', 800)),
                    'mileage': int(means.get('mileage', 100000)),
                    'vehicle_age': round(means.get('vehicle_age', 10.0), 1)
                },
                'primary_symptoms': top_symptoms
            })
        return catalog

    def get_fault_detail(self, fault_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve full deep diagnostic detail for a single fault."""
        if fault_name not in self.fault_knowledge:
            return None
        info = self.fault_knowledge[fault_name].copy()
        count = self.fault_counts.get(fault_name, 0)
        pct = round((count / self.total_records) * 100, 1) if self.total_records else 0
        means = self.fault_means.get(fault_name, {})
        symptoms_means = self.fault_symptoms.get(fault_name, {})

        top_symptoms = [
            {'symptom': s.replace('_', ' ').title(), 'prevalence': round(prob * 100, 1)}
            for s, prob in symptoms_means.items() if prob > 0.05
        ]
        top_symptoms.sort(key=lambda x: x['prevalence'], reverse=True)

        info.update({
            'dataset_count': count,
            'dataset_percentage': pct,
            'sensor_means': {
                'engine_temperature': round(means.get('engine_temperature', 90.0), 1),
                'battery_voltage': round(means.get('battery_voltage', 12.6), 2),
                'rpm': int(means.get('rpm', 800)),
                'mileage': int(means.get('mileage', 100000)),
                'vehicle_age': round(means.get('vehicle_age', 10.0), 1)
            },
            'symptom_prevalence': top_symptoms,
            'normal_baseline': self.normal_baseline
        })
        return info

    def find_similar_dataset_records(self, input_features: Dict[str, Any], top_n: int = 4) -> List[Dict[str, Any]]:
        """
        Calculates weighted similarity against all rows in dataset.csv and returns
        the closest real records matching this vehicle's symptom and telemetry state.
        """
        df = self.dataset_df
        symptom_cols = [
            'engine_vibration', 'engine_overheating', 'poor_mileage',
            'starting_problem', 'check_engine_light', 'brake_noise',
            'battery_problem', 'low_power', 'abnormal_sound'
        ]

        # Calculate distances across rows
        # Symptom distance: Hamming distance with heavy weight
        symptom_matrix = df[symptom_cols].values
        input_symptoms = np.array([input_features.get(col, 0) for col in symptom_cols], dtype=float)
        symptom_diff = np.abs(symptom_matrix - input_symptoms)
        symptom_distance = np.sum(symptom_diff, axis=1) * 2.5

        # Sensor normalized Euclidean distance
        temp_diff = (df['engine_temperature'].values - input_features.get('engine_temperature', 90.0)) / 25.0
        volt_diff = (df['battery_voltage'].values - input_features.get('battery_voltage', 12.6)) / 2.0
        rpm_diff = (df['rpm'].values - input_features.get('rpm', 800)) / 400.0
        mileage_diff = (df['mileage'].values - input_features.get('mileage', 40000)) / 80000.0
        age_diff = (df['vehicle_age'].values - input_features.get('vehicle_age', 5)) / 10.0

        sensor_distance = np.sqrt(
            temp_diff ** 2 + volt_diff ** 2 + (rpm_diff * 0.5) ** 2 + (mileage_diff * 0.3) ** 2 + (age_diff * 0.3) ** 2
        )

        total_distance = symptom_distance + sensor_distance
        top_indices = np.argsort(total_distance)[:top_n]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            row = df.iloc[idx]
            dist = float(total_distance[idx])
            sim_score = max(50.0, min(99.4, round(100.0 / (1.0 + (dist * 0.35)), 1)))

            # Active symptoms in this dataset row
            row_symptoms = [
                col.replace('_', ' ').title()
                for col in symptom_cols if int(row[col]) == 1
            ]

            results.append({
                'rank': rank,
                'dataset_row_index': int(idx) + 2, # matching 1-based CSV line with header
                'fault': str(row['fault']),
                'similarity_score': sim_score,
                'active_symptoms': row_symptoms,
                'engine_temperature': round(float(row['engine_temperature']), 1),
                'battery_voltage': round(float(row['battery_voltage']), 2),
                'rpm': int(row['rpm']),
                'mileage': int(row['mileage']),
                'vehicle_age': int(row['vehicle_age'])
            })

        return results

    def compute_sensor_benchmarks(self, input_features: Dict[str, Any], fault_name: str) -> Dict[str, Any]:
        """
        Compare user vehicle's telemetry with normal reference and fault reference averages.
        """
        fault_means = self.fault_means.get(fault_name, self.normal_baseline)
        norm = self.normal_baseline

        u_temp = float(input_features.get('engine_temperature', 90.0))
        f_temp = float(fault_means.get('engine_temperature', 90.0))
        n_temp = float(norm['engine_temperature'])

        temp_status = "Optimal"
        if u_temp > 105:
            temp_status = "Critical Overheating"
        elif u_temp > 95:
            temp_status = "Elevated"
        elif u_temp < 70:
            temp_status = "Cold / Thermostat Stuck Open"

        u_volt = float(input_features.get('battery_voltage', 12.6))
        f_volt = float(fault_means.get('battery_voltage', 12.6))
        n_volt = float(norm['battery_voltage'])

        volt_status = "Nominal"
        if u_volt < 11.4:
            volt_status = "Critical Voltage Drop"
        elif u_volt < 12.2:
            volt_status = "Sub-optimal / Weak Charge"
        elif u_volt > 14.8:
            volt_status = "Overcharging Hazard"

        u_rpm = int(input_features.get('rpm', 800))
        f_rpm = int(fault_means.get('rpm', 800))
        n_rpm = int(norm['rpm'])

        rpm_status = "Normal Idle"
        if u_rpm > 1200:
            rpm_status = "High Idle Surge"
        elif u_rpm < 650:
            rpm_status = "Rough / Stalling Idle"

        return {
            'engine_temperature': {
                'user_value': round(u_temp, 1),
                'normal_avg': round(n_temp, 1),
                'fault_avg': round(f_temp, 1),
                'safe_range': '82°C – 96°C',
                'status': temp_status,
                'deviation': round(u_temp - n_temp, 1)
            },
            'battery_voltage': {
                'user_value': round(u_volt, 2),
                'normal_avg': round(n_volt, 2),
                'fault_avg': round(f_volt, 2),
                'safe_range': '12.4V – 14.4V',
                'status': volt_status,
                'deviation': round(u_volt - n_volt, 2)
            },
            'rpm': {
                'user_value': u_rpm,
                'normal_avg': n_rpm,
                'fault_avg': f_rpm,
                'safe_range': '700 – 900 RPM',
                'status': rpm_status,
                'deviation': u_rpm - n_rpm
            }
        }

    def generate_diagnostic_evidence(
        self,
        predicted_fault: str,
        input_features: Dict[str, Any],
        selected_symptoms: List[str]
    ) -> Dict[str, Any]:
        """
        Generate complete, exhaustive diagnostic evidence package linking
        the prediction to dataset records, statistical distributions, and mechanical guidance.
        """
        knowledge = self.fault_knowledge.get(predicted_fault, self.fault_knowledge.get('Normal', {})).copy()
        count = self.fault_counts.get(predicted_fault, 0)
        pct = round((count / self.total_records) * 100, 1) if self.total_records else 0

        # Similar records from dataset.csv
        closest_records = self.find_similar_dataset_records(input_features, top_n=4)

        # Sensor telemetry benchmarks
        benchmarks = self.compute_sensor_benchmarks(input_features, predicted_fault)

        # Matched DTC details from dtc_codes.csv
        dtc_details = []
        for code in knowledge.get('dtc_codes', []):
            match = self.dtc_df[self.dtc_df['dtc'] == code]
            if not match.empty:
                row = match.iloc[0]
                dtc_details.append({
                    'code': code,
                    'description': str(row['description']),
                    'category': str(row['category']),
                    'severity': str(row['severity']),
                    'causes': str(row['causes']),
                    'recommendation': str(row['recommendation'])
                })
            else:
                dtc_details.append({
                    'code': code,
                    'description': 'Diagnostic Trouble Code',
                    'category': knowledge.get('category', 'Powertrain'),
                    'severity': knowledge.get('severity', 'HIGH'),
                    'causes': ', '.join(knowledge.get('causes', [])[:2]),
                    'recommendation': knowledge.get('recommendation', 'Inspect circuit')
                })

        return {
            'fault': predicted_fault,
            'category': knowledge.get('category', 'Automotive Diagnostics'),
            'summary': knowledge.get('summary', ''),
            'danger_level': knowledge.get('danger_level', ''),
            'dataset_count': count,
            'dataset_percentage': pct,
            'total_dataset_records': self.total_records,
            'affected_components': knowledge.get('affected_components', []),
            'workshop_procedure': knowledge.get('workshop_procedure', []),
            'estimated_repair_time': knowledge.get('estimated_repair_time', '1-2 Hours'),
            'repair_difficulty': knowledge.get('repair_difficulty', 'Moderate'),
            'sensor_benchmarks': benchmarks,
            'closest_records': closest_records,
            'dtc_matches': dtc_details
        }

    def query_dataset_records(
        self,
        fault: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Paginated inspection of raw records from data/dataset.csv."""
        df = self.dataset_df
        if fault and fault != 'All':
            df = df[df['fault'] == fault]

        total = len(df)
        page = df.iloc[offset: offset + limit]

        records = []
        for idx, row in page.iterrows():
            rec = row.to_dict()
            rec['row_number'] = int(idx) + 2
            records.append(rec)

        return {
            'total': total,
            'offset': offset,
            'limit': limit,
            'fault_filter': fault or 'All',
            'records': records
        }

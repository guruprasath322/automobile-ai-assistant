import random
import time

class OBDSimulator:
    def __init__(self):
        self.dtc_list = ["P0301", "P0420", "P0171", "P0300", "P0113", "P0507", "None"]
        
    def get_live_data(self, fault_mode=None):
        """
        Generate simulated live OBD-II data.
        fault_mode: if provided, simulate data specific to a fault (e.g., 'Overheating')
        """
        data = {
            "RPM": random.randint(750, 850), # Normal idle
            "Engine Temperature": random.randint(88, 94), # Normal temp in C
            "Vehicle Speed": 0,
            "Throttle Position": random.randint(10, 15),
            "Battery Voltage": round(random.uniform(12.5, 12.8), 2),
            "DTC": "None"
        }
        
        if fault_mode == "Engine Misfire":
            data["RPM"] = random.randint(600, 1100) # Fluctuating RPM
            data["DTC"] = "P0301"
        elif fault_mode == "Cooling System Problem":
            data["Engine Temperature"] = random.randint(105, 120)
            data["DTC"] = "P0117"
        elif fault_mode == "Battery Problem":
            data["Battery Voltage"] = round(random.uniform(10.0, 11.5), 2)
            data["DTC"] = "P0562"
        elif fault_mode == "Random":
            if random.random() > 0.7:
                data["DTC"] = random.choice(self.dtc_list[:-1])
        
        return data

    def get_dtc_details(self, dtc_code):
        """Simple lookup for common DTC codes if CSV is not available"""
        dtc_db = {
            "P0301": {
                "description": "Cylinder 1 Misfire Detected",
                "causes": ["Spark plug", "Ignition coil", "Fuel injector"],
                "severity": "HIGH"
            },
            "P0420": {
                "description": "Catalyst System Efficiency Below Threshold",
                "causes": ["Catalytic converter", "Oxygen sensor", "Exhaust leak"],
                "severity": "MEDIUM"
            },
            "P0171": {
                "description": "System Too Lean (Bank 1)",
                "causes": ["Vacuum leak", "MAF sensor", "Fuel pump"],
                "severity": "MEDIUM"
            },
            "P0300": {
                "description": "Random or Multiple Cylinder Misfire Detected",
                "causes": ["Ignition system", "Fuel system", "Vacuum leak"],
                "severity": "HIGH"
            },
            "P0117": {
                "description": "Engine Coolant Temperature Sensor 1 Circuit Low",
                "causes": ["Coolant sensor", "Wiring", "Thermostat"],
                "severity": "HIGH"
            },
            "P0562": {
                "description": "System Voltage Low",
                "causes": ["Battery", "Alternator", "Voltage regulator"],
                "severity": "MEDIUM"
            }
        }
        return dtc_db.get(dtc_code, {
            "description": "Unknown Trouble Code",
            "causes": ["Generic sensor or circuit issue"],
            "severity": "LOW"
        })

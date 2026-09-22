import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helpers import calculate_health_score
from obd.simulator import OBDSimulator
from database.database import AutomobileDB


class TestAutomobileAssistant(unittest.TestCase):
    def setUp(self):
        self.simulator = OBDSimulator()
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = AutomobileDB(db_path=self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_health_score_perfect(self):
        """Test health score when all parameters are optimal."""
        score, deductions = calculate_health_score(
            active_dtcs="None",
            engine_temp=90,
            battery_voltage=12.6,
            mileage=50000,
            last_fault_severity="LOW"
        )
        self.assertEqual(score, 100)
        self.assertEqual(len(deductions), 0)

    def test_health_score_with_faults(self):
        """Test health score deduction calculations."""
        score, deductions = calculate_health_score(
            active_dtcs="P0301",
            engine_temp=110,
            battery_voltage=11.0,
            mileage=120000,
            last_fault_severity="HIGH"
        )
        # Expected: 100 - 20 (DTC) - 15 (Temp) - 15 (Battery) - 20 (Severity) - 5 (Mileage) = 25
        self.assertEqual(score, 25)
        self.assertTrue(len(deductions) >= 4)

    def test_obd_simulator_normal(self):
        """Test normal live OBD telemetry generation."""
        data = self.simulator.get_live_data()
        self.assertIn("RPM", data)
        self.assertIn("Engine Temperature", data)
        self.assertIn("Battery Voltage", data)
        self.assertIn("DTC", data)
        self.assertGreaterEqual(data["RPM"], 700)
        self.assertLessEqual(data["RPM"], 900)

    def test_obd_simulator_fault_modes(self):
        """Test OBD telemetry under fault conditions."""
        misfire_data = self.simulator.get_live_data(fault_mode="Engine Misfire")
        self.assertEqual(misfire_data["DTC"], "P0301")

        overheat_data = self.simulator.get_live_data(fault_mode="Cooling System Problem")
        self.assertEqual(overheat_data["DTC"], "P0117")
        self.assertGreaterEqual(overheat_data["Engine Temperature"], 105)

    def test_dtc_lookup(self):
        """Test DTC code lookup details."""
        details = self.simulator.get_dtc_details("P0301")
        self.assertEqual(details["severity"], "HIGH")
        self.assertIn("Spark plug", details["causes"])

    def test_database_vehicle_and_diagnosis_operations(self):
        """Test SQLite vehicle registration and diagnosis history tracking."""
        vehicle = {
            "registration_number": "TN-42-AB-1234",
            "manufacturer": "Hyundai",
            "model": "i20",
            "manufacturing_year": 2021,
            "fuel_type": "Petrol",
            "transmission_type": "Manual",
            "current_mileage": 45000,
            "last_service_date": "2026-01-15"
        }
        self.db.save_vehicle(vehicle)
        fetched = self.db.get_vehicle("TN-42-AB-1234")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["model"], "i20")

        diagnosis = {
            "timestamp": "2026-09-22 21:00:00",
            "vehicle": "TN-42-AB-1234",
            "symptoms": ["Engine Misfire", "Rough Idle"],
            "predicted_fault": "Spark Plug Issue",
            "confidence": 0.94,
            "severity": "HIGH",
            "recommendation": "Inspect and replace spark plugs."
        }
        self.db.save_diagnosis(diagnosis)
        history = self.db.get_diagnosis_history("TN-42-AB-1234")
        self.assertEqual(len(history), 1)
        self.assertEqual(history.iloc[0]["predicted_fault"], "Spark Plug Issue")


if __name__ == "__main__":
    unittest.main()

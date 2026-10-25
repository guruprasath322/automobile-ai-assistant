import unittest
import sys
import os
import tempfile
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, db


class TestAutomobileAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Ensure a test vehicle exists
        self.test_vehicle = {
            "registration_number": "TEST-REG-9999",
            "manufacturer": "Toyota",
            "model": "Camry",
            "manufacturing_year": 2022,
            "fuel_type": "Hybrid",
            "transmission_type": "Automatic",
            "current_mileage": 30000,
            "last_service_date": "2026-01-01"
        }
        self.client.post("/api/vehicles", json=self.test_vehicle)

    def tearDown(self):
        # Clean up test vehicle
        self.client.delete("/api/vehicles/TEST-REG-9999")

    def test_root_index_html(self):
        """Test root serves the web application HTML page."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Automobile AI Assistant", response.text)
        self.assertIn("nav-tabs", response.text)

    def test_get_vehicles(self):
        """Test retrieving all registered vehicles."""
        response = self.client.get("/api/vehicles")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("vehicles", data)
        regs = [v["registration_number"] for v in data["vehicles"]]
        self.assertIn("TEST-REG-9999", regs)

    def test_active_vehicle(self):
        """Test switching and retrieving the active vehicle."""
        post_res = self.client.post("/api/active-vehicle", json={"registration_number": "TEST-REG-9999"})
        self.assertEqual(post_res.status_code, 200)
        self.assertEqual(post_res.json()["active_vehicle"]["registration_number"], "TEST-REG-9999")

        get_res = self.client.get("/api/active-vehicle")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["vehicle"]["registration_number"], "TEST-REG-9999")

    def test_obd_live_telemetry(self):
        """Test OBD-II telemetry simulation endpoint."""
        response = self.client.get("/api/obd/live?fault_mode=Normal")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("telemetry", data)
        self.assertIn("RPM", data["telemetry"])
        self.assertIn("Engine Temperature", data["telemetry"])
        self.assertIn("Battery Voltage", data["telemetry"])

    def test_dtc_lookup(self):
        """Test DTC details lookup endpoint."""
        response = self.client.get("/api/obd/dtc/P0301")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["dtc"], "P0301")
        self.assertIn("description", data["details"])
        self.assertEqual(data["details"]["severity"], "HIGH")

    def test_voice_extraction(self):
        """Test NLP keyword symptom extraction endpoint."""
        payload = {"text": "My car engine is overheating and making knocking sound"}
        response = self.client.post("/api/voice/extract", json=payload)
        self.assertEqual(response.status_code, 200)
        symptoms = response.json()["symptoms"]
        self.assertIn("Engine overheating", symptoms)
        self.assertIn("Knocking sound", symptoms)

    def test_diagnose_ai_mode(self):
        """Test diagnosis in AI Machine Learning model mode."""
        payload = {
            "vehicle_reg": "TEST-REG-9999",
            "mode": "ai",
            "symptoms": ["Engine vibration", "Engine overheating"],
            "engine_temp": 115,
            "rpm": 1200,
            "battery_voltage": 12.2,
            "mileage": 30000,
            "dtc_code": "P0117"
        }
        response = self.client.post("/api/diagnose", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("fault", data["diagnosis"])
        self.assertIn("confidence", data["diagnosis"])
        self.assertIn("severity", data["diagnosis"])
        self.assertIsNotNone(data["report_filename"])

    def test_diagnose_rule_mode(self):
        """Test diagnosis in Rule-Based mode."""
        payload = {
            "vehicle_reg": "TEST-REG-9999",
            "mode": "rule",
            "symptoms": ["Engine overheating"],
            "engine_temp": 112,
            "rpm": 850,
            "battery_voltage": 12.5,
            "mileage": 30000
        }
        response = self.client.post("/api/diagnose", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["diagnosis"]["fault"], "Cooling System Problem")
        self.assertEqual(data["diagnosis"]["severity"], "HIGH")

    def test_health_score_endpoint(self):
        """Test vehicle health score calculation."""
        response = self.client.get("/api/health-score?vehicle_reg=TEST-REG-9999")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("score", data)
        self.assertIn("deductions", data)
        self.assertIn("reminders", data)

    def test_maintenance_checklist_endpoint(self):
        """Test prioritized maintenance recommendations."""
        response = self.client.get("/api/maintenance/checklist?vehicle_reg=TEST-REG-9999")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["vehicle"]["registration_number"], "TEST-REG-9999")
        self.assertIn("checklist", data)
        self.assertIsInstance(data["checklist"], list)

    def test_dashboard_stats(self):
        """Test high-level dashboard aggregate metrics."""
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["total_vehicles"], 1)
        self.assertIn("health_score", data)


if __name__ == "__main__":
    unittest.main()

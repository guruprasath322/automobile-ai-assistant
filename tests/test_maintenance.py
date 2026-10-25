import unittest
from datetime import date

from utils.maintenance import generate_maintenance_checklist


class TestMaintenanceChecklist(unittest.TestCase):
    def test_flags_health_and_interval_items(self):
        checklist = generate_maintenance_checklist(
            mileage=65000,
            engine_temp=110,
            battery_voltage=11.7,
            last_service_date="2025-01-01",
            today=date(2026, 1, 1),
        )

        services = {item["service"] for item in checklist}
        self.assertIn("Cooling system inspection", services)
        self.assertIn("Battery and charging-system test", services)
        self.assertIn("Brake pad and rotor inspection", services)
        self.assertIn("Battery and alternator diagnostic", services)
        self.assertIn("Schedule a routine service", services)

    def test_healthy_recently_serviced_vehicle_has_no_actions(self):
        checklist = generate_maintenance_checklist(
            mileage=5000,
            engine_temp=90,
            battery_voltage=12.6,
            last_service_date="2026-01-01",
            today=date(2026, 2, 1),
        )

        self.assertEqual(checklist, [])


if __name__ == "__main__":
    unittest.main()

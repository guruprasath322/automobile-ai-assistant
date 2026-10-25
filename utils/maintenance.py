"""Maintenance checklist rules shared by the API and other integrations."""

from datetime import date, datetime
from typing import Optional


def generate_maintenance_checklist(
    mileage: int,
    engine_temp: float,
    battery_voltage: float,
    last_service_date: Optional[str],
    today: Optional[date] = None,
) -> list[dict[str, str]]:
    """Return prioritized maintenance actions based on vehicle health signals."""
    checklist: list[dict[str, str]] = []

    def add(service: str, reason: str, priority: str) -> None:
        checklist.append({
            "service": service,
            "reason": reason,
            "priority": priority,
        })

    if engine_temp > 105:
        add("Cooling system inspection", "Engine temperature is above 105°C.", "urgent")
    if battery_voltage < 12.0:
        add("Battery and charging-system test", "Battery voltage is below 12.0 V.", "high")
    if mileage >= 10000:
        add("Engine oil and filter change", "The vehicle has reached the 10,000 km service interval.", "medium")
    if mileage >= 40000:
        add("Brake pad and rotor inspection", "The vehicle has reached the 40,000 km inspection interval.", "medium")
    if mileage >= 60000:
        add("Battery and alternator diagnostic", "The vehicle has reached the 60,000 km diagnostic interval.", "low")
    if mileage >= 80000:
        add("Spark plug and transmission-fluid service", "The vehicle has reached the 80,000 km service interval.", "low")

    if last_service_date:
        try:
            service_date = datetime.strptime(last_service_date, "%Y-%m-%d").date()
        except ValueError:
            service_date = None
        reference_date = today or date.today()
        if service_date and (reference_date - service_date).days >= 180:
            add("Schedule a routine service", "More than six months have passed since the last recorded service.", "medium")

    return checklist

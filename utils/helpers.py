def calculate_health_score(active_dtcs, engine_temp, battery_voltage, mileage, last_fault_severity):
    """
    Calculate a vehicle health score from 0-100.
    """
    score = 100
    deductions = []
    
    # 1. DTC Deductions
    if active_dtcs and active_dtcs != "None":
        score -= 20
        deductions.append("Active Diagnostic Trouble Code (-20)")
        
    # 2. Temperature Deductions
    if engine_temp > 105:
        score -= 15
        deductions.append("High Engine Temperature (-15)")
    elif engine_temp > 100:
        score -= 5
        deductions.append("Elevated Engine Temperature (-5)")
        
    # 3. Battery Voltage Deductions
    if battery_voltage < 11.5:
        score -= 15
        deductions.append("Low Battery Voltage (-15)")
    elif battery_voltage < 12.0:
        score -= 5
        deductions.append("Weak Battery Voltage (-5)")
        
    # 4. Severity Deductions
    severity_map = {
        'CRITICAL': 30,
        'HIGH': 20,
        'MEDIUM': 10,
        'LOW': 0
    }
    sev_deduction = severity_map.get(last_fault_severity, 0)
    if sev_deduction > 0:
        score -= sev_deduction
        deductions.append(f"Last Fault Severity: {last_fault_severity} (-{sev_deduction})")
        
    # 5. Mileage Deduction (Aging)
    if mileage > 200000:
        score -= 10
        deductions.append("High Mileage Aging (-10)")
    elif mileage > 100000:
        score -= 5
        deductions.append("Moderate Mileage Aging (-5)")
        
    # Ensure score stays between 0-100
    score = max(0, min(100, score))
    
    return score, deductions

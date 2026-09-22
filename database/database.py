import sqlite3
import pandas as pd
import os
from pathlib import Path

class AutomobileDB:
    def __init__(self, db_path=None):
        project_root = Path(__file__).resolve().parents[1]
        db_dir = project_root / 'database'
        db_dir.mkdir(parents=True, exist_ok=True)

        if db_path is None:
            db_path = db_dir / 'automobile_assistant.db'

        self.db_path = str(db_path)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize the database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table for Vehicle Information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                registration_number TEXT PRIMARY KEY,
                manufacturer TEXT,
                model TEXT,
                manufacturing_year INTEGER,
                fuel_type TEXT,
                transmission_type TEXT,
                current_mileage INTEGER,
                last_service_date TEXT
            )
        ''')
        
        # Table for Diagnosis History
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnosis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                vehicle_reg TEXT,
                symptoms TEXT,
                predicted_fault TEXT,
                confidence REAL,
                severity TEXT,
                recommendation TEXT,
                FOREIGN KEY (vehicle_reg) REFERENCES vehicles (registration_number)
            )
        ''')
        
        conn.commit()
        conn.close()

    # --- Vehicle Operations ---
    
    def save_vehicle(self, vehicle_info):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO vehicles 
            (registration_number, manufacturer, model, manufacturing_year, fuel_type, transmission_type, current_mileage, last_service_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            vehicle_info['registration_number'],
            vehicle_info['manufacturer'],
            vehicle_info['model'],
            vehicle_info['manufacturing_year'],
            vehicle_info['fuel_type'],
            vehicle_info['transmission_type'],
            vehicle_info['current_mileage'],
            vehicle_info['last_service_date']
        ))
        conn.commit()
        conn.close()

    def get_vehicle(self, registration_number):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM vehicles WHERE registration_number = ?", conn, params=(registration_number,))
        conn.close()
        return df.to_dict('records')[0] if not df.empty else None

    def get_all_vehicles(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM vehicles", conn)
        conn.close()
        return df

    # --- Diagnosis Operations ---
    
    def save_diagnosis(self, diagnosis_record):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnosis_history 
            (timestamp, vehicle_reg, symptoms, predicted_fault, confidence, severity, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            diagnosis_record['timestamp'],
            diagnosis_record['vehicle'],
            ", ".join(diagnosis_record['symptoms']),
            diagnosis_record['predicted_fault'],
            diagnosis_record['confidence'],
            diagnosis_record['severity'],
            diagnosis_record['recommendation']
        ))
        conn.commit()
        conn.close()

    def get_diagnosis_history(self, vehicle_reg=None):
        conn = self.get_connection()
        if vehicle_reg:
            df = pd.read_sql_query("SELECT * FROM diagnosis_history WHERE vehicle_reg = ? ORDER BY timestamp DESC", conn, params=(vehicle_reg,))
        else:
            df = pd.read_sql_query("SELECT * FROM diagnosis_history ORDER BY timestamp DESC", conn)
        conn.close()
        return df

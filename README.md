[# AI Automobile Health & Diagnosis Assistant 🚗🤖

[![CI](https://github.com/guruprasath-s-b/automobile-ai-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/guruprasath-s-b/automobile-ai-assistant/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive AI/ML-powered decision-support system for vehicle health monitoring and fault diagnosis. This project is designed as a prototype for educational and college-level demonstrations (B.Tech AIML).

## 🌟 Overview

The **AI Automobile Health & Diagnosis Assistant** bridges the gap between complex automotive telemetry and user-friendly diagnostics. By leveraging Machine Learning, OBD-II simulation, and natural language processing, the system helps vehicle owners identify potential issues, understand their severity, and receive actionable maintenance recommendations.

## 🚀 Key Features

- **🤖 AI-Powered Diagnosis**: Uses Random Forest and Decision Tree models to predict vehicle faults with confidence scores.
- **📡 OBD-II Monitor**: Live simulation of engine metrics (RPM, Temperature, Voltage, Speed) and DTC (Diagnostic Trouble Code) detection with animated SVG instruments.
- **📊 Vehicle Health Score**: A dynamic 0-100 score based on real-time sensor data and historical diagnosis.
- **🎤 Voice Assistant**: Browser Web Speech API & natural language symptom extraction from spoken/typed descriptions.
- **📋 Persistent History**: SQLite database integration to track vehicle profiles and diagnosis history across sessions.
- **📄 Professional Reports**: Instant PDF report generation for every diagnosis.
- **🔧 Maintenance Reminders**: Smart alerts based on vehicle mileage and service history.
- **✅ Maintenance Checklist API**: Prioritized service actions based on live telemetry, mileage, and service age.

## 🛠️ Technology Stack

- **Frontend**: Modern HTML5, Responsive Vanilla CSS (Obsidian Dark Glassmorphism), Vanilla JavaScript (SPA)
- **Backend**: FastAPI & Uvicorn (Asynchronous REST API)
- **Machine Learning**: Scikit-learn (Random Forest, Decision Tree), Pandas, NumPy
- **Database**: SQLite
- **Reporting**: ReportLab (PDF Generation)
- **Voice**: Web Speech API & Keyword NLP extraction

## 📂 Project Structure

```text
automobile-ai-assistant/
├── app.py                    # Main FastAPI application server & REST API
├── requirements.txt          # Project dependencies
├── static/                   # Modern web frontend SPA
│   ├── index.html            # Single Page Application HTML
│   ├── css/style.css         # Cyber-obsidian design system & animations
│   └── js/app.js             # Real-time state & API communication
├── data/
│   ├── dataset.csv           # Synthetic training dataset
│   └── dtc_codes.csv         # DTC lookup database
├── ml/
│   ├── train_model.py        # ML training script
│   └── prediction.py         # AI inference engine
├── models/
│   ├── diagnosis_model.pkl   # Trained Random Forest model
│   └── feature_names.pkl     # ML feature metadata
├── obd/
│   └── simulator.py          # OBD-II simulation logic
├── database/
│   ├── database.py           # SQLite helper script
│   └── automobile_assistant.db # Persistent database file
├── reports/                  # Generated PDF reports
├── tests/                    # Automated unit test suite
│   ├── test_assistant.py     # Domain logic unit tests
│   └── test_api.py           # REST API endpoint tests
├── voice/                    # Voice processing logic
├── utils/                    # Health score & helper utilities
└── docs/                     # Step-by-step phase documentation
```

## ⚙️ Installation & Setup

1. **Clone the project**:
   ```bash
   git clone https://github.com/guruprasath-s-b/automobile-ai-assistant.git
   cd automobile-ai-assistant
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Unit Tests**:
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py"
   ```
4. **Train the ML Model** (optional, pre-trained model included):
   ```bash
   python3 ml/train_model.py
   ```
5. **Run the Web Application**:
   ```bash
   python3 app.py
   ```
   Open your browser and navigate to: `http://localhost:8000`

## 🧪 Usage Workflow

1. **Register**: Add your vehicle details in the "Vehicle Registration" page.
2. **Monitor**: Check live engine metrics in the "OBD-II Monitor".
3. **Diagnose**: Select symptoms manually or use the "Voice Simulation" to describe the issue.
4. **Analyze**: Review the AI prediction, confidence score, and severity level.
5. **Report**: Download the PDF report for your records.
6. **Health**: Check the "Vehicle Health" page for your 0-100 score and maintenance tips.
7. **Checklist**: Call `GET /api/maintenance/checklist` to receive prioritized maintenance actions for the active vehicle.

## ⚠️ Safety Disclaimer

This application is a **decision-support prototype** for educational purposes only. It is NOT a replacement for a professional mechanical diagnosis. Always consult a qualified technician for critical vehicle issues. Never ignore dashboard warning lights or unusual vehicle behavior.

## 🎓 Project Info

- **Domain**: Artificial Intelligence & Machine Learning
- **Algorithm**: Random Forest Classifier
- **Accuracy**: ~90%
- **Dataset**: Synthetic Automobile Fault Dataset (1,500 records)
- **Author**: [GURUPRASATH S B](https://github.com/guruprasath-s-b)

---
Developed for AI/ML Vehicle Health & Diagnostics.
](https://github.com/guruprasath322/automobile-ai-assistant)

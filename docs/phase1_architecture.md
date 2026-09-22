# Phase 1: Project Architecture, Software Requirements, and Folder Structure

## 1. What We Are Building
We are designing a comprehensive **AI Automobile Health & Diagnosis Assistant** tailored for college students (B.Tech AI/ML). This application bridges automotive diagnostics with machine learning, providing an interactive web-based dashboard built with **Streamlit**, backed by **SQLite**, powered by **scikit-learn** for predictive fault diagnosis, and equipped with OBD-II simulation, voice input, and PDF reporting.

## 2. Why We Need It
Modern vehicles are complex computerized systems. When a check engine light illuminates or unusual symptoms occur, vehicle owners often lack clarity on severity, causes, or urgency. This system provides a transparent, decision-support prototype that evaluates symptoms, OBD-II Diagnostic Trouble Codes (DTCs), and vehicle telemetry to predict potential faults, estimate health scores, and recommend professional actions.

## 3. Required Software & Installation Steps
To run this project on your local machine, ensure you have the following installed:
- **Python 3.10+** (Python programming language)
- **pip** (Python package installer)

### Installation Commands:
Open your terminal in the project directory and install the required dependencies:
```bash
pip install streamlit pandas numpy scikit-learn matplotlib plotly reportlab SpeechRecognition pyttsx3 pyserial
```

## 4. Exact Folder Structure
```text
automobile-ai-assistant/
│
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # Complete project documentation
│
├── data/
│   ├── dataset.csv           # Synthetic automobile fault dataset
│   └── dtc_codes.csv         # DTC lookup database
│
├── models/
│   ├── diagnosis_model.pkl   # Trained ML model
│   └── label_encoder.pkl     # Label encoder for fault classes
│
├── ml/
│   ├── train_model.py        # Script to train Decision Tree / Random Forest
│   └── prediction.py         # Prediction logic & confidence scoring
│
├── obd/
│   ├── simulator.py          # OBD-II simulation data generator
│   └── obd_reader.py         # Real ELM327 serial reader (optional)
│
├── database/
│   └── database.py           # SQLite connection and CRUD operations
│
├── voice/
│   └── speech.py             # Speech-to-text integration
│
├── reports/
│   └── report_generator.py   # PDF diagnosis report generator
│
└── utils/
    └── helpers.py            # Health score calculator & formatting helpers
```

## 5. How to Run Phase 1 (Architecture & Setup)
1. Ensure your folder structure matches the above.
2. Review this architecture document to understand the modular design.
3. Proceed to **Phase 2** where we implement Version 1 (Vehicle Form, Symptom Selection, and Rule-Based Diagnosis).

## 6. Common Beginner Errors and Solutions
- **ModuleNotFoundError**: Ensure you run `pip install -r requirements.txt` and activate your virtual environment if applicable.
- **Port already in use**: Streamlit runs on port 8501 by default. If occupied, run `streamlit run app.py --server.port 8502`.

# College Project Documentation: AI Automobile Health & Diagnosis Assistant

This document provides the structured content required for a B.Tech AIML college project report.

---

## 1. Problem Statement
Modern vehicles are equipped with complex Electronic Control Units (ECUs) that generate vast amounts of data. However, standard vehicle owners often struggle to interpret "Check Engine" lights or unusual symptoms. Existing diagnostic tools are either too technical for laypeople or require expensive hardware. There is a need for an accessible, AI-powered system that can bridge this gap by providing human-readable diagnosis, severity assessments, and health tracking.

## 2. Objectives
- To develop a web-based assistant for vehicle fault diagnosis.
- To implement a Machine Learning model (Random Forest) capable of predicting faults based on symptoms and sensor data.
- To simulate OBD-II telemetry for real-time health monitoring.
- To provide persistent storage for vehicle profiles and diagnosis history using SQLite.
- To generate professional diagnostic reports in PDF format.
- To simplify user interaction through voice-based symptom extraction.

## 3. Existing System
- **Manual Inspection**: Relies entirely on the expertise of a mechanic, which can be subjective and time-consuming.
- **Basic OBD-II Scanners**: Provide raw DTC codes (e.g., P0301) without explaining causes, severity, or next steps to the user.
- **Manufacturer Apps**: Often restricted to specific brands and lack advanced AI-based predictive capabilities for multi-symptom analysis.

## 4. Proposed System
The proposed system uses a **Random Forest Classifier** to analyze a combination of user-reported symptoms and simulated OBD-II sensor data. It provides:
- **Predictive Diagnosis**: Moves beyond simple code-lookup to pattern-based fault detection.
- **Severity Assessment**: Categorizes issues from LOW to CRITICAL to guide user urgency.
- **Educational Explanations**: Uses AI to explain "why" a fault was predicted in simple terms.
- **Holistic Health Scoring**: Aggregates multiple data points into a single 0-100 health metric.

## 5. Methodology
1. **Data Collection**: Generation of a synthetic dataset (1,500 records) mapping symptoms and sensor readings to 8 fault classes.
2. **Preprocessing**: Feature engineering of categorical symptoms and normalization of sensor data (RPM, Temp, Voltage).
3. **Model Selection**: Comparison between Decision Tree and Random Forest classifiers.
4. **Training**: Supervised learning using an 80/20 train-test split.
5. **Integration**: Embedding the trained model into a Streamlit web application.
6. **Persistence**: Implementation of a relational database (SQLite) for data lifecycle management.

## 6. System Architecture
The system follows a modular architecture:
- **Presentation Layer**: Streamlit UI for user interaction.
- **Logic Layer**: Python scripts for ML inference, OBD simulation, and voice processing.
- **Data Layer**: SQLite database for history and CSV files for DTC/Dataset storage.
- **External Integration**: ReportLab for PDF generation and Google Speech API for transcription.

## 7. ML Algorithm: Random Forest
Random Forest was chosen for its robustness and ability to handle both categorical (symptoms) and numerical (sensor) data.
- **Mechanism**: It creates an ensemble of multiple Decision Trees, where each tree is trained on a random subset of data.
- **Advantage**: Reduces overfitting and provides higher accuracy compared to a single Decision Tree.
- **Output**: Provides a probability distribution across fault classes, allowing for the calculation of a **Confidence Score**.

## 8. Results & Discussion
- **Accuracy**: The model achieved an accuracy of **90%** on the test dataset.
- **Performance**: High precision was observed in detecting critical faults like "Engine Misfire" and "Cooling System Problem."
- **User Impact**: The system successfully simplified complex DTC codes into actionable advice, reducing user anxiety and improving maintenance awareness.

## 9. Conclusion
The AI Automobile Health & Diagnosis Assistant demonstrates the practical application of Machine Learning in the automotive domain. By combining predictive modeling with real-time simulation, the project provides a comprehensive tool for vehicle health management, suitable for educational purposes and as a foundation for real-world diagnostic applications.

## 10. Future Scope
- **Real Hardware Integration**: Connecting to a physical ELM327 Bluetooth adapter for live vehicle data.
- **Deep Learning**: Implementing Neural Networks for sound-based engine fault detection (Audio Analysis).
- **Cloud Integration**: Syncing diagnosis history across multiple devices via a cloud backend.
- **Predictive Maintenance**: Using time-series analysis to predict when a part will fail before it actually does.

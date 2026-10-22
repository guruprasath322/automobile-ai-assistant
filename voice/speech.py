try:
    import speech_recognition as sr
except ImportError:
    sr = None

def transcribe_speech():
    """
    Attempt to transcribe speech from the microphone.
    Note: This requires a working microphone and PyAudio installed.
    For the web app, we use browser Web Speech API with text-based fallback.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
    except Exception as e:
        return f"Error: {str(e)}"

def extract_symptoms_from_text(text):
    """
    Simple keyword extraction to map spoken words to symptoms.
    """
    text = text.lower()
    symptom_keywords = {
        "vibration": "Engine vibration",
        "shaking": "Engine vibration",
        "hot": "Engine overheating",
        "overheating": "Engine overheating",
        "start": "Engine not starting",
        "starting": "Engine not starting",
        "stalling": "Engine stalling",
        "power": "Low engine power",
        "acceleration": "Poor acceleration",
        "mileage": "Poor mileage",
        "fuel": "High fuel consumption",
        "noise": "Brake noise",
        "brake": "Brake noise",
        "battery": "Battery problem",
        "light": "Warning light",
        "clicking": "Clicking sound",
        "grinding": "Grinding sound",
        "knocking": "Knocking sound",
        "whistling": "Whistling sound"
    }
    
    found_symptoms = []
    for keyword, symptom in symptom_keywords.items():
        if keyword in text:
            found_symptoms.append(symptom)
            
    return list(set(found_symptoms))

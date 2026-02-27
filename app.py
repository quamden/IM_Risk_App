import streamlit as st
import re

st.title("IM Risk Parser")

hpi_text = st.text_area("Paste HPI Here")

# HEART score helpers
def extract_age(text):
    match = re.search(r'(\d+)[- ]?year[- ]?old', text.lower())
    return int(match.group(1)) if match else None

def extract_troponin(text):
    match = re.search(r'troponin.*?(\d+\.?\d*)', text.lower())
    return float(match.group(1)) if match else None

def count_risk_factors(text):
    factors = ["hypertension","htn","diabetes","dm","smoker","hyperlipidemia","hld","family history","obesity"]
    return sum(1 for f in factors if f in text.lower())

def detect_ecg_changes(text):
    t = text.lower()
    if "st depression" in t or "st elevation" in t:
        return "significant"
    elif "nonspecific" in t:
        return "nonspecific"
    return "normal"

def calculate_heart(age, rf_count, troponin, ecg):
    score = 0
    if age: score += 2 if age>=65 else 1 if age>=45 else 0
    score += 2 if rf_count>=3 else 1 if rf_count>=1 else 0
    if troponin: score += 2 if troponin>0.1 else 1 if troponin>0.04 else 0
    score += 2 if ecg=="significant" else 1 if ecg=="nonspecific" else 0
    return score

# TIMI (simplified)
def calculate_timi(text):
    return sum([
        1 if "age>65" in text.lower() else 0,
        1 if "≥3 risk factors" in text.lower() else 0,
        1 if "known coronary artery disease" in text.lower() else 0,
        1 if "aspirin use last 7 days" in text.lower() else 0,
        1 if "severe angina" in text.lower() else 0,
        1 if "st deviation" in text.lower() else 0,
        1 if "positive cardiac marker" in text.lower() else 0
    ])

# ASCVD (very simplified example)
def calculate_ascvd(text):
    return sum([
        1 if "male" in text.lower() else 0,
        1 if "age>40" in text.lower() else 0,
        1 if "hypertension" in text.lower() else 0,
        1 if "diabetes" in text.lower() else 0,
        1 if "smoker" in text.lower() else 0,
        1 if "hyperlipidemia" in text.lower() else 0
    ])

if st.button("Calculate Scores"):
    age = extract_age(hpi_text)
    troponin = extract_troponin(hpi_text)
    rf_count = count_risk_factors(hpi_text)
    ecg = detect_ecg_changes(hpi_text)

    st.write("### Extracted Data")
    st.write("Age:", age)
    st.write("Troponin:", troponin)
    st.write("Risk Factors Found:", rf_count)
    st.write("ECG Interpretation:", ecg)

    heart_score = calculate_heart(age, rf_count, troponin, ecg)
    st.write("## HEART Score:", heart_score)
    if heart_score <= 3: st.success("Low Risk")
    elif heart_score <= 6: st.warning("Moderate Risk")
    else: st.error("High Risk")

    timi_score = calculate_timi(hpi_text)
    st.write("## TIMI Score:", timi_score)

    ascvd_score = calculate_ascvd(hpi_text)
    st.write("## ASCVD Risk (simplified points):", ascvd_score)

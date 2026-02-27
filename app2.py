import streamlit as st
import re

st.title("Comprehensive Cardio Risk Parser")

hpi_text = st.text_area("Paste HPI Here", height=250)

# -----------------------
# Abbreviation mappings
# -----------------------
abbreviations = {
    "htn": "hypertension",
    "dm": "diabetes",
    "hld": "hyperlipidemia",
    "cad": "coronary artery disease",
    "af": "atrial fibrillation",
    "ckd": "chronic kidney disease",
    "mi": "myocardial infarction",
    "stemi": "ST elevation myocardial infarction",
    "nstemi": "non-ST elevation myocardial infarction",
    "copd": "chronic obstructive pulmonary disease",
}

def expand_abbreviations(text):
    t = text.lower()
    for abbr, full in abbreviations.items():
        t = re.sub(r'\b'+abbr+r'\b', full, t)
    return t

# -----------------------
# Helper functions
# -----------------------
def extract_age(text):
    match = re.search(r'(\d+)[- ]?year[- ]?old', text.lower())
    return int(match.group(1)) if match else None

def detect_gender(text):
    text = text.lower()
    if "male" in text:
        return "male"
    elif "female" in text:
        return "female"
    return None

def count_risk_factors(text, factors):
    count = 0
    for f in factors:
        if f in text.lower():
            count += 1
    return count

def extract_troponin(text):
    match = re.search(r'troponin.*?(\d+\.?\d*)', text.lower())
    return float(match.group(1)) if match else None

def detect_ecg(text):
    t = text.lower()
    if "st elevation" in t or "st depression" in t:
        return "significant"
    elif "nonspecific" in t:
        return "nonspecific"
    return "normal"

# -----------------------
# HEART Score
# -----------------------
def calculate_heart(age, risk_count, troponin, ecg):
    score = 0
    if age:
        score += 2 if age >= 65 else 1 if age >= 45 else 0
    score += 2 if risk_count >= 3 else 1 if risk_count >= 1 else 0
    if troponin:
        score += 2 if troponin > 0.1 else 1 if troponin > 0.04 else 0
    score += 2 if ecg == "significant" else 1 if ecg == "nonspecific" else 0
    return score

# -----------------------
# TIMI Score (simplified)
# -----------------------
def calculate_timi(text):
    text = text.lower()
    return sum([
        1 if "age>65" in text or "age >=65" in text else 0,
        1 if "≥3 risk factors" in text or "3+ risk factors" in text else 0,
        1 if "known coronary artery disease" in text or "cad" in text else 0,
        1 if "aspirin last 7 days" in text or "aspirin use" in text else 0,
        1 if "severe angina" in text else 0,
        1 if "st deviation" in text or "st elevation" in text or "st depression" in text else 0,
        1 if "positive cardiac marker" in text or "troponin" in text else 0
    ])

# -----------------------
# GRACE Score (simplified points for demo)
# -----------------------
def calculate_grace(text):
    text = text.lower()
    points = 0
    points += 5 if "age>65" in text else 0
    points += 3 if "hr>100" in text else 0
    points += 3 if "sbp<100" in text else 0
    points += 2 if "creatinine" in text else 0
    points += 2 if "st deviation" in text else 0
    points += 3 if "troponin" in text else 0
    return points

# -----------------------
# ASCVD (simplified)
# -----------------------
def calculate_ascvd(text, age, gender):
    text = text.lower()
    points = 0
    if gender == "male": points += 1
    if age and age > 40: points += 1
    points += 1 if "hypertension" in text else 0
    points += 1 if "diabetes" in text else 0
    points += 1 if "smoker" in text else 0
    points += 1 if "hyperlipidemia" in text else 0
    return points

# -----------------------
# CHA2DS2-VASc Score
# -----------------------
def calculate_cha2ds2_vasc(text, age, gender):
    text = text.lower()
    score = 0
    if age:
        score += 2 if age >= 75 else 1 if age >= 65 else 0
    score += 1 if gender=="female" else 0
    score += 1 if "hypertension" in text else 0
    score += 1 if "diabetes" in text else 0
    score += 1 if "stroke" in text or "tia" in text else 0
    score += 1 if "vascular disease" in text or "cad" in text else 0
    return score

# -----------------------
# HAS-BLED Score (simplified)
# -----------------------
def calculate_has_bled(text):
    text = text.lower()
    score = 0
    score += 1 if "hypertension" in text else 0
    score += 1 if "abnormal liver" in text or "abnormal kidney" in text or "ckd" in text else 0
    score += 1 if "stroke" in text else 0
    score += 1 if "bleeding" in text else 0
    score += 1 if "labile inr" in text else 0
    score += 1 if "age>65" in text else 0
    score += 1 if "drugs" in text or "alcohol" in text else 0
    return score

# -----------------------
# SYNTAX II Score (simplified points demo)
# -----------------------
def calculate_syntax2(text, age, gender):
    text = text.lower()
    score = 0
    score += 2 if age and age>70 else 0
    score += 1 if gender=="female" else 0
    score += 2 if "ckd" in text else 0
    score += 1 if "left main disease" in text else 0
    score += 1 if "3 vessel disease" in text else 0
    return score

# -----------------------
# Main app logic
# -----------------------
if st.button("Calculate Scores"):

    hpi_expanded = expand_abbreviations(hpi_text)
    age = extract_age(hpi_expanded)
    gender = detect_gender(hpi_expanded)
    risk_factors = ["hypertension","diabetes","hyperlipidemia","smoker","family history","cad"]
    rf_count = count_risk_factors(hpi_expanded, risk_factors)
    troponin = extract_troponin(hpi_expanded)
    ecg = detect_ecg(hpi_expanded)

    st.write("### Extracted Data")
    st.write("Age:", age)
    st.write("Gender:", gender)
    st.write("Risk Factors Found:", rf_count)
    st.write("Troponin:", troponin)
    st.write("ECG Interpretation:", ecg)

    st.write("## Scores")
    st.write("HEART Score:", calculate_heart(age, rf_count, troponin, ecg))
    st.write("TIMI Score:", calculate_timi(hpi_expanded))
    st.write("GRACE Score (simplified points):", calculate_grace(hpi_expanded))
    st.write("ASCVD Risk Points (simplified):", calculate_ascvd(hpi_expanded, age, gender))
    st.write("CHA2DS2-VASc Score:", calculate_cha2ds2_vasc(hpi_expanded, age, gender))
    st.write("HAS-BLED Score:", calculate_has_bled(hpi_expanded))
    st.write("SYNTAX II Score (simplified points):", calculate_syntax2(hpi_expanded, age, gender))

import streamlit as st
import re

st.title("Comprehensive Cardiovascular Risk Calculator")

# -----------------------
# Input HPI
# -----------------------
hpi_text = st.text_area("Paste HPI here:", height=300)

# -----------------------
# Abbreviation mapping
# -----------------------
abbreviations = {
    "htn": "hypertension",
    "dm": "diabetes",
    "hld": "hyperlipidemia",
    "cad": "coronary artery disease",
    "af": "atrial fibrillation",
    "ckd": "chronic kidney disease",
    "mi": "myocardial infarction",
    "tia": "TIA",
    "copd": "chronic obstructive pulmonary disease",
    "ob": "obesity"
}

def expand_abbreviations(text):
    t = text.lower()
    for abbr, full in abbreviations.items():
        t = re.sub(r'\b'+abbr+r'\b', full, t)
    return t

# -----------------------
# Extract basic info
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

def extract_risk_factors(text, factors):
    return [f for f in factors if f in text.lower()]

def extract_troponin(text):
    match = re.search(r'troponin.*?(\d+\.?\d*)', text.lower())
    return float(match.group(1)) if match else None

def detect_ecg(text):
    t = text.lower()
    if "st elevation" in t or "st depression" in t:
        return "ST deviation"
    elif "nonspecific" in t:
        return "nonspecific"
    return "normal"

# -----------------------
# Scores calculations (simplified)
# -----------------------
def calculate_heart(age, risk_count, troponin, ecg):
    score = 0
    if age:
        score += 2 if age >= 65 else 1 if age >= 45 else 0
    score += 2 if risk_count >= 3 else 1 if risk_count >= 1 else 0
    if troponin:
        score += 2 if troponin > 0.1 else 1 if troponin > 0.04 else 0
    score += 2 if ecg == "ST deviation" else 1 if ecg == "nonspecific" else 0
    return score

def calculate_timi(text):
    text = text.lower()
    return sum([
        1 if "age >=65" in text or "age>65" in text else 0,
        1 if "≥3 risk factors" in text else 0,
        1 if "cad" in text else 0,
        1 if "st deviation" in text else 0,
        1 if "anginal events" in text else 0,
        1 if "aspirin" in text else 0,
        1 if "troponin" in text else 0
    ])

def calculate_grace(text):
    # Simplified points based on presence of key words
    points = 0
    text = text.lower()
    points += 5 if "age>65" in text else 0
    points += 3 if "hr>100" in text else 0
    points += 3 if "sbp<100" in text else 0
    points += 2 if "creatinine" in text else 0
    points += 2 if "killip" in text else 0
    points += 3 if "st deviation" in text else 0
    points += 3 if "troponin" in text else 0
    points += 5 if "cardiac arrest" in text else 0
    return points

def calculate_ascvd(age, gender, text):
    points = 0
    if gender=="male": points+=1
    if age and age>40: points+=1
    for factor in ["hypertension","diabetes","smoker","hyperlipidemia","family history"]:
        if factor in text.lower(): points+=1
    return points

def calculate_cha2ds2_vasc(age, gender, text):
    score = 0
    if age: score += 2 if age>=75 else 1 if age>=65 else 0
    if gender=="female": score+=1
    for factor in ["hypertension","diabetes","stroke","tia","vascular disease","cad"]: 
        if factor in text.lower(): score+=1
    return score

def calculate_has_bled(age, text):
    score = 0
    if age and age>65: score+=1
    for factor in ["hypertension","abnormal kidney","abnormal liver","stroke","bleeding","labile inr","drugs","alcohol"]:
        if factor in text.lower(): score+=1
    return score

def calculate_syntax(text):
    # Requires angiogram input; simplified demo points
    points = 0
    for factor in ["left main disease","3 vessel disease","total occlusions","bifurcation","trifurcation","calcification"]:
        if factor in text.lower(): points+=1
    return points

def calculate_h2fpef(text, age):
    score=0
    if "obesity" in text.lower(): score+=2
    if "hypertension" in text.lower(): score+=1
    if "atrial fibrillation" in text.lower(): score+=3
    if age and age>60: score+=1
    if "pulmonary hypertension" in text.lower(): score+=1
    if "filling pressure" in text.lower(): score+=1
    return score

# -----------------------
# Main
# -----------------------
if st.button("Calculate Scores"):
    hpi_expanded = expand_abbreviations(hpi_text)
    age = extract_age(hpi_expanded)
    gender = detect_gender(hpi_expanded)
    risk_factors = ["hypertension","diabetes","smoker","hyperlipidemia","family history","obesity"]
    rf_found = extract_risk_factors(hpi_expanded, risk_factors)
    troponin = extract_troponin(hpi_expanded)
    ecg = detect_ecg(hpi_expanded)

    st.write("### Extracted Data")
    st.write("Age:", age)
    st.write("Gender:", gender)
    st.write("Risk Factors Found:", rf_found)
    st.write("Troponin:", troponin)
    st.write("ECG:", ecg)

    st.write("## Scores")
    st.write("HEART Score:", calculate_heart(age, len(rf_found), troponin, ecg))
    st.write("TIMI Score:", calculate_timi(hpi_expanded))
    st.write("GRACE Score:", calculate_grace(hpi_expanded))
    st.write("ASCVD Score:", calculate_ascvd(age, gender, hpi_expanded))
    st.write("CHA2DS2-VASc Score:", calculate_cha2ds2_vasc(age, gender, hpi_expanded))
    st.write("HAS-BLED Score:", calculate_has_bled(age, hpi_expanded))
    st.write("SYNTAX Score (simplified):", calculate_syntax(hpi_expanded))
    st.write("H2FPEF Score (simplified):", calculate_h2fpef(hpi_expanded, age))

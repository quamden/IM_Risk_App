import streamlit as st
import re

st.title("Cardiovascular Risk Score Parser")

hpi_text = st.text_area("Paste HPI", height=250)

# -------------------------
# Abbreviation Expansion
# -------------------------

abbreviations = {
    "htn": "hypertension",
    "dm": "diabetes",
    "hld": "hyperlipidemia",
    "cad": "coronary artery disease",
    "af": "atrial fibrillation",
    "ckd": "chronic kidney disease",
    "mi": "myocardial infarction",
    "tia": "transient ischemic attack",
    "pad": "peripheral artery disease",
    "chf": "heart failure"
}

def expand_abbreviations(text):
    text = text.lower()
    for abbr, full in abbreviations.items():
        text = re.sub(r"\b"+abbr+r"\b", full, text)
    return text

# -------------------------
# Extract Basic Data
# -------------------------

def extract_age(text):
    match = re.search(r'(\d+)[- ]?year[- ]?old', text)
    return int(match.group(1)) if match else None

def detect_gender(text):
    if "female" in text:
        return "female"
    if "male" in text:
        return "male"
    return None

def detect_troponin(text):
    match = re.search(r"troponin.*?(\d+\.?\d*)", text)
    return float(match.group(1)) if match else None

def detect_ecg(text):
    if "st elevation" in text or "st depression" in text:
        return "st deviation"
    if "nonspecific" in text:
        return "nonspecific"
    return "normal"

# -------------------------
# HEART Score
# -------------------------

def heart_score(age, risk_count, troponin, ecg):

    b = {}

    if age is None:
        b["Age"] = 0
    elif age >= 65:
        b["Age"] = 2
    elif age >= 45:
        b["Age"] = 1
    else:
        b["Age"] = 0

    if risk_count >= 3:
        b["Risk Factors"] = 2
    elif risk_count >= 1:
        b["Risk Factors"] = 1
    else:
        b["Risk Factors"] = 0

    if troponin is None:
        b["Troponin"] = 0
    elif troponin > 0.1:
        b["Troponin"] = 2
    elif troponin > 0.04:
        b["Troponin"] = 1
    else:
        b["Troponin"] = 0

    if ecg == "st deviation":
        b["ECG"] = 2
    elif ecg == "nonspecific":
        b["ECG"] = 1
    else:
        b["ECG"] = 0

    return sum(b.values()), b

# -------------------------
# TIMI Score
# -------------------------

def timi_score(text, age):

    b = {}

    b["Age ≥65"] = 1 if age and age >= 65 else 0
    b["Known CAD"] = 1 if "coronary artery disease" in text else 0
    b["ST deviation"] = 1 if "st elevation" in text or "st depression" in text else 0
    b["Aspirin last 7 days"] = 1 if "aspirin" in text else 0
    b["Positive troponin"] = 1 if "troponin" in text else 0
    b["Recent angina"] = 1 if "angina" in text else 0
    b["≥3 risk factors"] = 1 if sum(x in text for x in ["hypertension","diabetes","smoking","hyperlipidemia","family history"]) >=3 else 0

    return sum(b.values()), b

# -------------------------
# GRACE Score (simplified)
# -------------------------

def grace_score(text, age):

    b = {}

    b["Age >65"] = 2 if age and age > 65 else 0
    b["Tachycardia"] = 1 if "heart rate 100" in text or "hr 100" in text else 0
    b["Low BP"] = 1 if "sbp <100" in text else 0
    b["Elevated Creatinine"] = 1 if "creatinine" in text else 0
    b["Killip class"] = 1 if "killip" in text else 0
    b["ST deviation"] = 1 if "st elevation" in text or "st depression" in text else 0
    b["Positive troponin"] = 1 if "troponin" in text else 0
    b["Cardiac arrest"] = 2 if "cardiac arrest" in text else 0

    return sum(b.values()), b

# -------------------------
# CHA2DS2VASc
# -------------------------

def cha2ds2vasc(text, age, gender):

    b = {}

    b["CHF"] = 1 if "heart failure" in text else 0
    b["Hypertension"] = 1 if "hypertension" in text else 0
    b["Diabetes"] = 1 if "diabetes" in text else 0
    b["Stroke/TIA"] = 2 if "stroke" in text or "transient ischemic attack" in text else 0
    b["Vascular disease"] = 1 if "coronary artery disease" in text or "peripheral artery disease" in text else 0

    if age:
        if age >= 75:
            b["Age"] = 2
        elif age >= 65:
            b["Age"] = 1
        else:
            b["Age"] = 0
    else:
        b["Age"] = 0

    b["Sex category"] = 1 if gender == "female" else 0

    return sum(b.values()), b

# -------------------------
# HAS-BLED
# -------------------------

def has_bled(text, age):

    b = {}

    b["Hypertension"] = 1 if "hypertension" in text else 0
    b["Renal disease"] = 1 if "chronic kidney disease" in text else 0
    b["Liver disease"] = 1 if "liver disease" in text else 0
    b["Stroke history"] = 1 if "stroke" in text else 0
    b["Bleeding history"] = 1 if "bleeding" in text else 0
    b["Labile INR"] = 1 if "labile inr" in text else 0
    b["Age >65"] = 1 if age and age > 65 else 0
    b["Drugs/alcohol"] = 1 if "alcohol" in text or "nsaid" in text else 0

    return sum(b.values()), b

# -------------------------
# H2FPEF
# -------------------------

def h2fpef(text, age):

    b = {}

    b["Obesity"] = 2 if "obesity" in text else 0
    b["≥2 antihypertensives"] = 1 if "two antihypertensive" in text else 0
    b["Atrial fibrillation"] = 3 if "atrial fibrillation" in text else 0
    b["Pulmonary hypertension"] = 1 if "pulmonary hypertension" in text else 0
    b["Age >60"] = 1 if age and age > 60 else 0
    b["Elevated filling pressure"] = 1 if "e/e" in text else 0

    return sum(b.values()), b

# -------------------------
# Run App
# -------------------------

if st.button("Calculate Scores"):

    text = expand_abbreviations(hpi_text)

    age = extract_age(text)
    gender = detect_gender(text)
    troponin = detect_troponin(text)
    ecg = detect_ecg(text)

    risk_factors = ["hypertension","diabetes","smoking","hyperlipidemia","family history","obesity"]
    risk_count = sum(r in text for r in risk_factors)

    st.header("Detected Clinical Data")

    st.write("Age:", age)
    st.write("Gender:", gender)
    st.write("Troponin:", troponin)
    st.write("ECG:", ecg)
    st.write("Risk factor count:", risk_count)

    scores = {
        "HEART Score": heart_score(age,risk_count,troponin,ecg),
        "TIMI Score": timi_score(text,age),
        "GRACE Score": grace_score(text,age),
        "CHA2DS2-VASc": cha2ds2vasc(text,age,gender),
        "HAS-BLED": has_bled(text,age),
        "H2FPEF": h2fpef(text,age)
    }

    for name,(total,details) in scores.items():

        st.subheader(name)
        st.write("Total Score:", total)

        for factor,points in details.items():
            st.write(f"{factor}: {points} points")

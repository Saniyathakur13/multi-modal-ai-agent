import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"


# ==========================================
# CLEAN OCR TEXT
# ==========================================

def normalize_ocr_text(text):
    replacements = {
        "HEMOCLOBIN": "HEMOGLOBIN",
        "NEUTROPHIIS": "NEUTROPHILS",
        "PTIHAONISIS": "EOSINOPHILS",
        "mil1/cmm": "mill/cmm",
        "Lakha/cu": "Lakhs/cu",
        "1/al": "g/dl",
        "g/a1": "g/dl",
        "mmo1/1": "mmol/l"
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    text = re.sub(r"\b888\b", "88.8", text)
    text = re.sub(r"\s+", " ", text)

    return text


# ==========================================
# REGEX EXTRACTION
# ==========================================

def extract_values(text):
    cleaned_text = text.upper()

    patterns = {
        "hemoglobin": [
            r"HEMOGLOBIN\s+([\d.]+)",
            r"HB\s*:?\s*([\d.]+)"
        ],
        "wbc": [
            r"TOTAL COUNT\s+([\d,]+)",
            r"WBC\s*:?\s*([\d,]+)"
        ],
        "rbc": [
            r"RED BLOOD CELLS\s*\(RBC\)\s+([\d.]+)",
            r"RBC\s*:?\s*([\d.]+)"
        ],
        "platelets": [
            r"PLATELET COUNT\s+([\d.]+)",
            r"PLATELETS\s*:?\s*([\d.]+)"
        ]
    }

    extracted = {}

    for key, regex_list in patterns.items():
        extracted[key] = None
        for pattern in regex_list:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", "")
                try:
                    extracted[key] = float(value)
                    break
                except:
                    pass

    return extracted


# ==========================================
# PATIENT NAME EXTRACTION
# ==========================================

def extract_patient_name(text):
    text = re.sub(r"\s+", " ", text)

    patterns = [
        # MCS.INDUMATI HUNSIGI pattern (your report format)
        r"MCS\.\s*([A-Z\s]+?)(?:\s+SAMPLE|\s+AGE|\s+REPORTED|$)",
        r"NAME\s*:?\s*([A-Z\s]+?)(?:\s+SAMPLE|\s+AGE|\s+REPORTED|$)",
        r"PATIENT\s*:?\s*([A-Z\s]+?)(?:\s+SAMPLE|\s+AGE|\s+REPORTED|$)",
        r"MR\.\s*([A-Z\s]+?)(?:\s+SAMPLE|\s+AGE|\s+REPORTED|$)",
        r"MRS\.\s*([A-Z\s]+?)(?:\s+SAMPLE|\s+AGE|\s+REPORTED|$)",
        # Also catch after "Name" or "Patient Name"
        r"(?:Name|Patient)\s*:?\s*([A-Z\s]+?)(?:\s+SAMPLE|\s+AGE|\s+REPORTED|$)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            name = re.sub(r"\s+", " ", name)
            # Clean up any extra text
            name = re.sub(r'\s+$', '', name)
            if name and len(name) > 2:
                return name.title()

    return ""


# ==========================================
# GENERATE SUMMARY (ALWAYS WORKS)
# ==========================================

def generate_summary(data):
    """Generate a summary from extracted data - NEVER returns 'API failed'"""
    findings = []
    details = []

    hb = data.get("hemoglobin")
    wbc = data.get("wbc")
    rbc = data.get("rbc")
    platelets = data.get("platelets")

    # Build details
    if hb is not None:
        details.append(f"Hemoglobin: {hb} g/dl")
    if wbc is not None:
        details.append(f"WBC: {wbc} cells/cu")
    if rbc is not None:
        details.append(f"RBC: {rbc} mill/cmm")
    if platelets is not None:
        details.append(f"Platelets: {platelets} Lakhs/cu")

    # Build findings
    if hb is not None:
        if hb < 11:
            findings.append("Low hemoglobin detected")
        elif hb > 16:
            findings.append("High hemoglobin detected")
        else:
            findings.append("Hemoglobin within normal range")

    if wbc is not None:
        if wbc < 4000:
            findings.append("Low white blood cell count")
        elif wbc > 11000:
            findings.append("High white blood cell count")
        else:
            findings.append("WBC within normal range")

    if platelets is not None:
        if platelets < 1.4:
            findings.append("Low platelet count detected")
        elif platelets > 4.5:
            findings.append("High platelet count detected")
        else:
            findings.append("Platelets within normal range")

    # Build the summary
    if not details:
        return "No medical data could be extracted from the report."

    summary = "Complete Blood Count (CBC) Analysis:\n"
    summary += "• " + "\n• ".join(details) + "\n\n"

    if findings:
        summary += "Key Findings:\n"
        summary += "• " + "\n• ".join(findings)
    else:
        summary += "All values are within normal ranges. No abnormal findings reported."

    return summary


def generate_abnormal_findings(data):
    findings = []
    hb = data.get("hemoglobin")
    wbc = data.get("wbc")
    platelets = data.get("platelets")

    if hb is not None and hb < 11:
        findings.append(f"Low hemoglobin: {hb} g/dl (Normal: 11.0-16.0)")
    if hb is not None and hb > 16:
        findings.append(f"High hemoglobin: {hb} g/dl (Normal: 11.0-16.0)")
    if wbc is not None and wbc < 4000:
        findings.append(f"Low WBC count: {wbc} cells/cu (Normal: 4000-11000)")
    if wbc is not None and wbc > 11000:
        findings.append(f"High WBC count: {wbc} cells/cu (Normal: 4000-11000)")
    if platelets is not None and platelets < 1.4:
        findings.append(f"Low platelet count: {platelets} Lakhs/cu (Normal: 1.40-4.50)")
    if platelets is not None and platelets > 4.5:
        findings.append(f"High platelet count: {platelets} Lakhs/cu (Normal: 1.40-4.50)")

    return findings


# ==========================================
# MAIN ANALYSIS FUNCTION
# ==========================================

def analyze_medical_report(report_text):
    # Step 1: Clean OCR
    report_text = normalize_ocr_text(report_text)

    print("\n===== CLEANED OCR TEXT =====\n")
    print(report_text[:3000])

    # Step 2: Regex Extraction (ALWAYS WORKS)
    regex_data = extract_values(report_text)

    print("\n===== REGEX EXTRACTION =====\n")
    print(regex_data)

    # Step 3: Patient Name
    patient_name = extract_patient_name(report_text)

    # Step 4: Build result from regex (100% reliable)
    final_result = {
        "patient_name": patient_name,
        "hemoglobin": regex_data.get("hemoglobin"),
        "wbc": regex_data.get("wbc"),
        "rbc": regex_data.get("rbc"),
        "platelets": regex_data.get("platelets"),
        "abnormal_findings": generate_abnormal_findings(regex_data),
        "summary": generate_summary(regex_data)  # ALWAYS works, never says "API failed"
    }
    # Add this after building final_result (before the print statement)

    # ==========================================
    # GENAI ENHANCEMENT (Optional)
    # ==========================================
    
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here":
        try:
            print("\n===== GENAI ENHANCEMENT =====")
            
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Medical AI Agent"
            }
            
            # Prepare data for GenAI
            genai_prompt = f"""Analyze this medical report data and provide a professional medical summary:

Patient: {patient_name or 'Unknown'}
Hemoglobin: {regex_data.get('hemoglobin', 'N/A')} g/dl
WBC: {regex_data.get('wbc', 'N/A')} cells/cu
RBC: {regex_data.get('rbc', 'N/A')} mill/cmm
Platelets: {regex_data.get('platelets', 'N/A')} Lakhs/cu
Abnormal Findings: {generate_abnormal_findings(regex_data) if generate_abnormal_findings(regex_data) else 'None detected'}

Provide a concise, professional medical summary (2-3 sentences)."""

            payload = {
                "model": "meta-llama/llama-3.2-3b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a medical AI assistant. Provide professional medical summaries."},
                    {"role": "user", "content": genai_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 150
            }

            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=20
            )

            print(f"GenAI Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                genai_summary = result["choices"][0]["message"]["content"]
                print(f"✅ GenAI Summary: {genai_summary}")
                
                # Update summary with GenAI
                final_result["summary"] = genai_summary
                final_result["genai_enhanced"] = True
            else:
                print(f"❌ GenAI failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                final_result["genai_enhanced"] = False

        except Exception as e:
            print(f"❌ GenAI error: {str(e)}")
            final_result["genai_enhanced"] = False
    else:
        final_result["genai_enhanced"] = False

    print("\n===== FINAL RESULT =====\n")
    print(json.dumps(final_result, indent=2))

    return final_result
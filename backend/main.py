import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ocr_service import extract_text_from_image
from services.llm_service import analyze_medical_report

image_path = "uploads/report.png"

# OCR STEP
report_text = extract_text_from_image(image_path)

print("\n===== EXTRACTED OCR TEXT =====\n")
print(report_text)

# AI STEP
result = analyze_medical_report(report_text)

print("\n===== FINAL JSON OUTPUT =====\n")
print(result)
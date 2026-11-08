import numpy as np

# Monkey patch to fix imgaug compatibility with NumPy 2.0
if not hasattr(np, 'sctypes'):
    np.sctypes = {'int': [np.int8, np.int16, np.int32, np.int64],
                  'uint': [np.uint8, np.uint16, np.uint32, np.uint64],
                  'float': [np.float16, np.float32, np.float64],
                  'complex': [np.complex64, np.complex128],
                  'others': [bool, object, bytes, str, np.void]}

import streamlit as st
import os
import base64
from services.ocr_service import extract_text_from_image
from services.llm_service import analyze_medical_report

st.set_page_config(page_title="Medical AI Agent", page_icon="🏥", layout="wide")

def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("backend/style.css")

st.title("🏥 Medical AI Agent")
st.markdown("Upload a medical report image (PNG/JPG) to extract data and generate an AI summary.")

uploaded_file = st.file_uploader("Choose a medical report image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # 1. Read bytes
    image_bytes = uploaded_file.getvalue()
    
    # 2. THE FOOLPROOF IMAGE FIX: Display via Base64 HTML
    b64_img = base64.b64encode(image_bytes).decode()
    st.markdown(
        f'<img src="data:image/png;base64,{b64_img}" width="400" style="border-radius: 10px;">', 
        unsafe_allow_html=True
    )
    st.caption("Uploaded Report")
    
    if st.button("🔍 Analyze Report"):
        with st.spinner("Extracting text and analyzing..."):
            # Save temp file for OCR
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(image_bytes)
            
            # Step 1: OCR
            extracted_text = extract_text_from_image(temp_path)
            
            # Step 2: Analysis
            result = analyze_medical_report(extracted_text)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Display Results
            st.success("Analysis Complete!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 Patient Information")
                st.write(f"**Patient Name:** {result.get('patient_name') or 'N/A'}")
                st.write(f"**Hemoglobin:** {result.get('hemoglobin') or 'N/A'} g/dl")
                st.write(f"**WBC:** {result.get('wbc') or 'N/A'} cells/cu")
                st.write(f"**RBC:** {result.get('rbc') or 'N/A'} mill/cmm")
                st.write(f"**Platelets:** {result.get('platelets') or 'N/A'} Lakhs/cu")
            
            with col2:
                st.subheader("⚠️ Abnormal Findings")
                findings = result.get('abnormal_findings', [])
                if findings:
                    for f in findings:
                        st.error(f)
                else:
                    st.success("No abnormal findings detected.")
            
            st.subheader("🧠 AI Summary")
            st.info(result.get('summary'))
            
            with st.expander("📄 View Extracted OCR Text"):
                st.text(extracted_text)

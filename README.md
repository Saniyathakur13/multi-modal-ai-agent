# 🏥 Multi-Modal Medical AI Agent

An AI-powered medical report analysis system that extracts structured patient data from medical images using OCR, NLP, and Generative AI.

## ✨ Features
- **📤 Upload Medical Reports:** Drag and drop PNG/JPG images of medical reports.
- **🔍 OCR Extraction:** Uses PaddleOCR and OpenCV to preprocess and extract text from images.
- **📊 NLP Data Parsing:** Uses Regex (Named Entity Recognition) to extract Patient Name, Hemoglobin, WBC, RBC, and Platelets.
- **⚠️ Abnormal Detection:** Automatically flags values outside normal medical ranges.
- **🧠 GenAI Summary:** Uses OpenRouter LLM (Llama-3) to generate professional, natural-language medical summaries based on the extracted data.
- **🌐 Streamlit UI:** Clean, responsive web interface.

## 🛠️ Tech Stack
- **Backend:** Python, Streamlit
- **Computer Vision:** OpenCV, PaddleOCR
- **NLP:** Regex Pattern Matching, Text Normalization
- **Generative AI:** OpenRouter API (Llama-3.2-3b)
- **Deployment:** GitHub, Streamlit Community Cloud

## 🚀 How It Works
1. User uploads a medical report image.
2. OpenCV preprocesses the image (grayscale, denoising).
3. PaddleOCR extracts the raw text.
4. Regex parses structured data (e.g., Hemoglobin: 11.5).
5. Rule-based logic detects abnormal values.
6. Extracted data is sent to the OpenRouter LLM API to generate a natural-language summary.

## 💻 Local Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/multi-modal-ai-agent.git
   cd multi-modal-ai-agent
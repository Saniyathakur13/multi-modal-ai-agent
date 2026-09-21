from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ocr_service import extract_text_from_image
from services.llm_service import analyze_medical_report

app = FastAPI(title="Medical AI Agent", 
              description="Multi-Modal Medical Report Analysis")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads folder if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Get the frontend directory path
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

@app.get("/")
async def home():
    """Serve the main HTML page"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Serve CSS, JS, and other files from frontend
@app.get("/{filename}")
async def serve_static(filename: str):
    """Serve static files from frontend folder"""
    file_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "message": "Medical AI Agent Running"}

@app.post("/analyze-report")
async def analyze_report(file: UploadFile = File(...)):
    print(f"📥 STEP 1: FILE RECEIVED - {file.filename}")
    
    # Save uploaded file
    temp_path = f"uploads/temp_{file.filename}"
    contents = await file.read()
    
    with open(temp_path, "wb") as f:
        f.write(contents)
    
    print(f"💾 STEP 2: FILE SAVED - {temp_path}")
    
    # Extract text using OCR
    extracted_text = extract_text_from_image(temp_path)
    
    print("🔍 STEP 3: OCR COMPLETE")
    print("\n===== EXTRACTED OCR TEXT =====\n")
    print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
    
    # Analyze with LLM
    result = analyze_medical_report(extracted_text)
    
    print("🤖 STEP 4: AI ANALYSIS COMPLETE")
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    return {
        "status": "success",
        "filename": file.filename,
        "extracted_text": extracted_text,
        "structured_data": result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
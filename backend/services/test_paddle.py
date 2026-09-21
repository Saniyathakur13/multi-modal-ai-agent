from paddleocr import PaddleOCR
import cv2
import numpy as np
import os

print(f"✅ NumPy: {np.__version__}")
print(f"✅ OpenCV: {cv2.__version__}")

try:
    import paddle
    print(f"✅ Paddle: {paddle.__version__}")
except:
    print("❌ Paddle not found")

# Initialize PaddleOCR
try:
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    print("✅ PaddleOCR initialized successfully!")
    
    # Test with sample image
    if os.path.exists("uploads/report.png"):
        from services.ocr_service import extract_text_from_image
        text = extract_text_from_image("uploads/report.png")
        print(f"✅ OCR successful! Extracted {len(text)} characters")
        print("\n📝 First 300 characters:")
        print(text[:300])
    else:
        print("⚠️ No test image at uploads/report.png")
        
except Exception as e:
    print(f"❌ Error: {e}")
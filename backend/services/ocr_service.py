import os
import cv2
import logging

# Suppress all PaddleOCR logs
os.environ['FLAGS_log_level'] = '3'
os.environ['GLOG_v'] = '0'

# Disable logging for paddleocr
logging.getLogger('ppocr').setLevel(logging.ERROR)
logging.getLogger('paddleocr').setLevel(logging.ERROR)

from paddleocr import PaddleOCR

# Initialize PaddleOCR once at module load
print("🔧 Initializing PaddleOCR...")
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en',
    show_log=False  # CRITICAL: This suppresses the debug output
)
print("✅ PaddleOCR initialized successfully!")

def extract_text_from_image(image_path):
    """
    Extract text from image using PaddleOCR
    """
    try:
        img = cv2.imread(image_path)
        
        if img is None:
            return "Error: Could not read image"
        
        # Resize image for better OCR
        img = cv2.resize(img, None, fx=2, fy=2)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Light denoising
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Save processed image
        processed_path = "processed.png"
        cv2.imwrite(processed_path, gray)
        
        # OCR
        result = ocr.ocr(processed_path)
        
        extracted_text = ""
        
        if result and result[0]:
            for line in result[0]:
                extracted_text += line[1][0] + "\n"
        else:
            return "No text detected in image"
        
        # Clean up
        if os.path.exists(processed_path):
            os.remove(processed_path)
        
        return extracted_text
        
    except Exception as e:
        return f"Error in OCR: {str(e)}"

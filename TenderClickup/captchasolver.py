from PIL import Image
import pytesseract
import re
# Path to the tesseract executable
# You only need to specify this if it's not in your PATH

def ocr_from_image(img_path):
    image = Image.open(img_path)
    text = pytesseract.image_to_string(image)
    
    # Keep only alphanumeric characters
    clean_text = re.sub(r'[^a-zA-Z0-9]', '', text)
    
    return clean_text.strip()

if __name__ == "__main__":
    img_path = 'downloaded_captcha.png'
    recognized_text = ocr_from_image(img_path)
    print(recognized_text)
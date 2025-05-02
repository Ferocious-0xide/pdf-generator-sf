import requests
import json
import os
import subprocess
import tempfile
import sys
from PIL import Image, ImageChops

# Base URL for your Heroku app
API_URL = "https://barcode-pdf-generator-efeb33ff5fd5.herokuapp.com"

# Sample JSON payload (same as in test_base64_endpoint.py)
payload = {
    "barcodeBase64": "iVBORw0KGgoAAAANSUhEUgAAAZkAAACCAQAAAAC8uIiPAAAACXBIWXMAABcSAAAXEgFnn9JSAAAAEnRFWHRTb2Z0d2FyZQBCYXJjb2RlNEryjnYuAAABvklEQVR4Xu3TsWrcMBzHcV09eClRujUQ0JAX6JgsUR+l0CFzt06VoYOXgNcMgXuUOnhwh9Jn8KFCVx1ZdFTVr38lV2hlhTiFbn9tB9+POekvCSDqV6dH1fq6v5Rf37yewsWJrq4Oz/zR5z48/3Zhq2e1Pj17qa6Puy8HBwZoBCNGjBgxYsSIESNGjBgxYsSIESNGjBgxYvTf0JMXo/2aoSjjCpPBEIQJ9SRMA6ezZoac9BQqfCTkKkLC9DJrikg38g5NhD7Qrzprhm673dBr2ucBIObH/DhXLVj1swQOkSFMSbUgpBR0mZJCSEht/doS0jdZslDKCTU7dE2Sx5C3hKiU9ssRbSnbmfDCscKNp7rZUg7tbVB4LCGhTBykyUlFIzTlpAWFQY0aG+ypIS8cfK7/el1PdAx0nBXWVJCDmhHS1uj/zXScPsXWVJCtIWho4GmY+u8ke5dlpTQANhGmD26/8tfq4TaP5BMaMk1kr/ReguV0JAlBUSzpSwdRLchZOQSFDR0C7vzehyiotP79Oh7cuK9UIKuAr3Fvoo6CNU8/nLvkEwIUx11Gq7KmjLqNd3UCl7RVW/Qm6yZoSXr39AvKgBwgEJ01wkAAAAASUVORK5CYII=",
    "date": "05/01/2025",
    "service": "MJG",
    "sku": "Y",
    "jewelryType": "Ring",
    "statedWeight": 1.00,
    "statedCount": 5,
    "requestedEngraving": "kevin rulz",
    "reportNumber": "A1PBV"
}

def verify_barcodes():
    """Test both endpoints and compare the results visually"""
    print("Step 1: Getting the original barcode image...")
    
    # Get the original image
    response = requests.post(
        f"{API_URL}/verify_base64_image",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"Error getting original image: {response.status_code}")
        print(response.text)
        return
    
    # Save the original image
    original_path = "original_barcode.png"
    with open(original_path, "wb") as f:
        f.write(response.content)
    print(f"Original image saved as {original_path}")
    
    print("\nStep 2: Getting the PDF with embedded barcode...")
    
    # Get the PDF
    response = requests.post(
        f"{API_URL}/generate_pdf_from_base64",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"Error getting PDF: {response.status_code}")
        print(response.text)
        return
    
    # Save the PDF
    pdf_path = "verification_barcode.pdf"
    with open(pdf_path, "wb") as f:
        f.write(response.content)
    print(f"PDF saved as {pdf_path}")
    
    print("\nStep 3: Visual verification instructions")
    print("1. Open the original_barcode.png file to see the original barcode")
    print("2. Open the verification_barcode.pdf file to see the PDF with embedded barcode")
    print("3. Visually compare the barcodes to ensure they match")
    print("\nNote: For more advanced verification, you'll need to install ImageMagick")
    print("and adjust the script to extract the barcode from the PDF.")

if __name__ == "__main__":
    verify_barcodes()
    
    print("\nVerification complete!") 
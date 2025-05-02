import requests
import json
import os

# Base URL for your Heroku app
API_URL = "https://barcode-pdf-generator-efeb33ff5fd5.herokuapp.com"

# Sample JSON payload (similar to what Salesforce would send)
payload = {
    "reportNumber": "123456",
    "date": "2025-05-01",
    "service": "testing",
    "sku": "123uu543u",
    "jewelryType": "earrings",
    "statedWeight": "14.5 g",
    "statedCount": "2",
    "requestedEngraving": "test engraving"
}

def test_pdf_endpoint():
    """Test the PDF generation endpoint"""
    print("Testing PDF generation endpoint...")
    
    response = requests.post(
        f"{API_URL}/generate_barcode_pdf",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        # Save the PDF
        with open("test_barcode.pdf", "wb") as f:
            f.write(response.content)
        print(f"PDF saved successfully as test_barcode.pdf")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_image_endpoint():
    """Test the image generation endpoint"""
    print("Testing image generation endpoint...")
    
    response = requests.post(
        f"{API_URL}/generate_barcode_image",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        # Save the image
        with open("test_barcode.png", "wb") as f:
            f.write(response.content)
        print(f"Image saved successfully as test_barcode.png")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def list_saved_barcodes():
    """List all saved barcodes in the database"""
    print("Listing all saved barcodes...")
    
    response = requests.get(f"{API_URL}/barcodes")
    
    if response.status_code == 200:
        barcodes = response.json()
        print(f"Found {len(barcodes)} barcodes:")
        for barcode in barcodes:
            print(f"ID: {barcode['id']}, Report Number: {barcode['report_number']}, Date: {barcode['date']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test PDF generation
    test_pdf_endpoint()
    
    # Test image generation
    test_image_endpoint()
    
    # List all saved barcodes
    list_saved_barcodes()
    
    print("\nTesting complete!")
    print("You can check the resulting files to see if they contain the correct barcodes.") 
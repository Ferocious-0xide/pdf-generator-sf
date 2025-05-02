import requests
import json
import os

def test_barcode_api_local():
    url = "http://localhost:8080/generate_barcode_pdf"
    
    # Test data matching the expected payload from Salesforce
    payload = {
        "barcodeBase64": "",  # Empty as we'll use the ReportLab-generated barcode
        "date": "05/01/2025",
        "service": "MJG",
        "sku": "Y",
        "jewelryType": "Ring",
        "statedWeight": 1.00,
        "statedCount": 5,
        "requestedEngraving": "kevin rulz",
        "reportNumber": "A1PBV"
    }
    
    # Send request to the API
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    
    # Save the PDF to a file
    if response.status_code == 200:
        with open("test_barcode.pdf", "wb") as f:
            f.write(response.content)
        print(f"PDF saved as test_barcode.pdf")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_barcode_api_local() 
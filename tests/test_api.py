import requests
import json
import os

def test_local_api():
    url = "http://localhost:8080/generate_barcode_pdf"
    
    # Test payload matching the sample from Salesforce
    payload = {
        "barcodeBase64": "",  # Empty for now, will use the generated barcode
        "date": "05/01/2025",
        "service": "MJG",
        "sku": "Y",
        "jewelryType": "Ring",
        "statedWeight": 1.00,
        "statedCount": 5,
        "requestedEngraving": "kevin rulz",
        "reportNumber": "A1PBV"
    }
    
    headers = {"Content-Type": "application/json"}
    
    print("Sending request to API...")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        output_file = "test_output.pdf"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Success! PDF saved as {output_file}")
        print(f"Full path: {os.path.abspath(output_file)}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # First check if server is running
    try:
        health_response = requests.get("http://localhost:8080/health")
        if health_response.status_code == 200:
            print("Server is running, proceeding with test...")
            test_local_api()
        else:
            print("Server health check failed.")
    except requests.exceptions.ConnectionError:
        print("ERROR: Server is not running. Please start the server first with 'python src/barcode_image_pdf.py'") 
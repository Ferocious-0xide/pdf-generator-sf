import requests
import json
import os
from datetime import datetime

# Base URL for your Heroku app
API_URL = "https://barcode-pdf-generator-efeb33ff5fd5.herokuapp.com"

# Sample JSON payload as Salesforce will send
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

def test_salesforce_api():
    """Test the generate_pdf_from_base64 endpoint that Salesforce will use"""
    print("Testing generate_pdf_from_base64 endpoint for Salesforce integration...")
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Send request to the API
    print(f"Sending request to {API_URL}/generate_pdf_from_base64...")
    response = requests.post(
        f"{API_URL}/generate_pdf_from_base64",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    # Check status and save PDF if successful
    if response.status_code == 200:
        # Save the PDF
        pdf_filename = f"salesforce_barcode_{timestamp}.pdf"
        with open(pdf_filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Success! PDF saved as {pdf_filename}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        # Also test listing endpoint to verify data was saved
        print("\nVerifying data was saved to database by checking /barcodes endpoint...")
        list_response = requests.get(f"{API_URL}/barcodes")
        
        if list_response.status_code == 200:
            barcodes = list_response.json()
            # Look for matching report number in response
            found = False
            for barcode in barcodes:
                if barcode['report_number'] == payload['reportNumber']:
                    found = True
                    print(f"✅ Data successfully stored in database with ID: {barcode['id']}")
                    break
            
            if not found:
                print("❌ Could not verify data was stored in database")
        else:
            print(f"❌ Error checking database: {list_response.status_code}")
            print(list_response.text)
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test the Salesforce integration endpoint
    test_salesforce_api()
    
    print("\nTest complete!") 
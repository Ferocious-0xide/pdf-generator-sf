import requests
import json
import os

# Base URL for your Heroku app
API_URL = "https://barcode-pdf-generator-efeb33ff5fd5.herokuapp.com"

# Sample JSON payload exactly as Salesforce will send
payload = {
    "barcodeBase64": "iVBORw0KGgoAAAANSUhEUgAAAZkAAACCAQAAAAC8uIiPAAAACXBIWXMAABcSAAAXEgFnn9JSAAAAEnRFWHRTb2Z0d2FyZQBCYXJjb2RlNEryjnYuAAABvklEQVR4Xu3TsWrcMBzHcV09eClRujUQ0JAX6JgsUR+l0CFzt06VoYOXgNcMgXuUOnhwh9Jn8KFCVx1ZdFTVr38lV2hlhTiFbn9tB9+POekvCSDqV6dH1fq6v5Rf37yewsWJrq4Oz/zR5z48/3Zhq2e1Pj17qa6Puy8HBwZoBCNGjBgxYsSIESNGjBgxYsSIESNGjBj9N/TkxWi/ZijKuMJkMARhQj0J08DprJkhJz2FCh8JuYqQML3MmiLSjbxDE6EP9KvOmhm67XZBr2ucBIObH/DhXLVj1swQOkSFMSbUgpBR0mZJCSGht/doS0jdZslDKCTU7dE2Sx5C3hKiU9ssRbSnbmfDCscKNp7rZUg7tbVB4LCGhTBykyUlFIzTlpAWFQY0aG+ypIS8cfK7/el1PdAx0nBXWVJCDmhHS1uj/zXScPsXWVJCtIWho4GmY+u8ke5dlpTQANhGmD26/8pfq4TaP5BMaMk1kr/ReguV0JAlBUSzpSwdRLchZOQSFDR0C7vzehyiotP79Oh7cuK9UIKuAr3Fvoo6CNU8/nLvkEwIUx11Gq7KmjLqNd3UCl7RVW/Qm6yZoSXr39AvKgBwgEJ01wkAAAAASUVORK5CYII=",
    "date": "05/01/2025",
    "service": "MJG",
    "sku": "Y",
    "jewelryType": "Ring",
    "statedWeight": 1.00,
    "statedCount": 5,
    "requestedEngraving": "kevin rulz",
    "reportNumber": "A1PBV"
}

def test_base64_endpoint():
    """Test the endpoint that accepts base64 barcode data"""
    print("Testing generate_pdf_from_base64 endpoint...")
    
    response = requests.post(
        f"{API_URL}/generate_pdf_from_base64",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        # Save the PDF
        with open("test_base64_barcode.pdf", "wb") as f:
            f.write(response.content)
        print(f"PDF saved successfully as test_base64_barcode.pdf")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test the new endpoint
    test_base64_endpoint()
    
    print("\nTesting complete!")
    print("You can check the resulting file to verify it contains the correct barcode.") 
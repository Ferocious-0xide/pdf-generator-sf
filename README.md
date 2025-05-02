# Barcode PDF Generator

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3117/)
[![Docker](https://img.shields.io/badge/docker-supported-2496ED.svg?logo=docker)](https://www.docker.com/)
[![Heroku](https://img.shields.io/badge/heroku-ready-430098.svg?logo=heroku)](https://heroku.com)

A Python service that generates 3"x3" PDF barcodes from JSON payloads. Designed to work with Salesforce flows.

## Requirements

- Python 3.9+
- Flask
- Pillow
- Python-barcode
- ReportLab

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the application

### Local development

```bash
python src/barcode_image_pdf.py
```

This will start the service on http://localhost:8080

### Using Docker

Build the Docker image:
```bash
docker build -t barcode-pdf-generator .
```

Run the container:
```bash
docker run -p 8080:8080 barcode-pdf-generator
```

Or use Docker Compose:
```bash
docker-compose up -d
```

### Deploying to Heroku

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login to Heroku:
   ```bash
   heroku login
   ```
3. Create a new Heroku app:
   ```bash
   heroku create barcode-pdf-generator
   ```
4. Deploy to Heroku:
   ```bash
   git push heroku main
   ```
5. Open your application:
   ```bash
   heroku open
   ```

## API Usage

The service provides the following endpoints:

```
POST /generate_barcode_pdf    # Generates a PDF with a code128 barcode
POST /generate_barcode_image  # Generates a PNG image
POST /generate_pdf_from_base64  # Generates a PDF from a base64-encoded barcode (for Salesforce)
GET /health                   # Health check endpoint
GET /barcodes                 # Lists all saved barcodes
GET /barcodes/<id>            # Gets a specific barcode by ID
GET /barcodes/<id>/regenerate_pdf   # Regenerates a PDF from saved data
GET /barcodes/<id>/regenerate_image # Regenerates an image from saved data
```

### Request body (JSON):

```json
{
  "barcodeBase64": "",  # Optional: base64-encoded barcode image
  "date": "05/01/2025",
  "service": "MJG",
  "sku": "Y",
  "jewelryType": "Ring",
  "statedWeight": 1.00,
  "statedCount": 5,
  "requestedEngraving": "kevin rulz",
  "reportNumber": "A1PBV"
}
```

### Response:

The API returns either a PDF file or PNG image with a 3"x3" barcode label, depending on the endpoint used.

## Salesforce Integration

To integrate with Salesforce, use the `/generate_pdf_from_base64` endpoint which is specifically designed to accept base64-encoded barcode images from Salesforce. 

### Integration Details for Salesforce Team

#### API Endpoint URL:
```
https://barcode-pdf-generator-efeb33ff5fd5.herokuapp.com/generate_pdf_from_base64
```

#### HTTP Method:
- POST

#### Headers:
- Content-Type: application/json

#### Request Payload Format:
```json
{
  "barcodeBase64": "[base64-encoded-barcode-image]",
  "date": "05/01/2025",
  "service": "MJG",
  "sku": "Y",
  "jewelryType": "Ring",
  "statedWeight": 1.00,
  "statedCount": 5,
  "requestedEngraving": "kevin rulz",
  "reportNumber": "A1PBV"
}
```

#### Response:
- Content-Type: application/pdf
- Body: Binary PDF file

#### Sample cURL Command (for testing):
```
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"barcodeBase64":"iVBORw0KGgoAAAANSUhEUgAAAZkAAACCAQAAAAC8uIiPAAAACXBIWXMAABcSAAAXEgFnn9JSAAAAEnRFWHRTb2Z0d2FyZQBCYXJjb2RlNEryjnYuAAABvklEQVR4Xu3TsWrcMBzHcV09eClRujUQ0JAX6JgsUR+l0CFzt06VoYOXgNcMgXuUOnhwh9Jn8KFCVx1ZdFTVr38lV2hlhTiFbn9tB9+POekvCSDqV6dH1fq6v5Rf37yewsWJrq4Oz/zR5z48/3Zhq2e1Pj17qa6Puy8HBwZoBCNGjBgxYsSIESNGjBgxYsSIESNGjBgxYvTf0JMXo/2aoSjjCpPBEIQJ9SRMA6ezZoac9BQqfCTkKkLC9DJrikg38g5NhD7Qrzprhm673dBr2ucBIObH/DhXLVj1swQOkSFMSbUgpBR0mZJCSEht/doS0jdZslDKCTU7dE2Sx5C3hKiU9ssRbSnbmfDCscKNp7rZUg7tbVB4LCGhTBykyUlFIzTlpAWFQY0aG+ypIS8cfK7/el1PdAx0nBXWVJCDmhHS1uj/zXScPsXWVJCtIWho4GmY+u8ke5dlpTQANhGmD26/8tfq4TaP5BMaMk1kr/ReguV0JAlBUSzpSwdRLchZOQSFDR0C7vzehyiotP79Oh7cuK9UIKuAr3Fvoo6CNU8/nLvkEwIUx11Gq7KmjLqNd3UCl7RVW/Qm6yZoSXr39AvKgBwgEJ01wkAAAAASUVORK5CYII=","date":"05/01/2025","service":"MJG","sku":"Y","jewelryType":"Ring","statedWeight":1.00,"statedCount":5,"requestedEngraving":"kevin rulz","reportNumber":"A1PBV"}' \
  -o salesforce_test.pdf \
  https://barcode-pdf-generator-efeb33ff5fd5.herokuapp.com/generate_pdf_from_base64
```

#### Important Notes:
- The endpoint expects the barcode image to be properly base64 encoded
- All fields shown in the example payload are expected
- The response is a PDF file that can be saved directly
- There is no authentication currently implemented
- The endpoint stores the data in the database for future reference

#### Troubleshooting:
- If you receive a 500 error, check that your payload matches the expected format
- For debugging issues, contact the API administrator

### General Salesforce Integration

To integrate with Salesforce Flow:
1. Deploy this service to an accessible endpoint
2. In your Salesforce Flow, use the "HTTP Request" action to make a POST request to the `/generate_pdf_from_base64` endpoint
3. Include the JSON payload with all required fields
4. Handle the PDF response in your flow

## Project Structure

```
barcode_pdf/
├── src/                 # Source code
│   ├── __init__.py      # Package initialization
│   └── barcode_image_pdf.py  # Main application module
├── tests/               # Test scripts
│   ├── test_api.py      # API test
│   ├── test_barcode.py  # Barcode generation test
│   └── test_curl.sh     # cURL test script
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── Procfile             # Heroku process file
└── runtime.txt          # Heroku Python runtime specification
```

## Testing

To test the API locally:

```bash
python tests/test_api.py
```

This will generate a PDF file named `test_output.pdf` in the current directory.

To test the Salesforce integration:

```bash
python test_salesforce_api.py
```

This will test the `/generate_pdf_from_base64` endpoint and verify that it works correctly.

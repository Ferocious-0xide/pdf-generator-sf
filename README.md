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
POST /generate_barcode_pdf  # Generates a PDF file
POST /generate_barcode_image  # Generates a PNG image
GET /health  # Health check endpoint
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

## Salesforce Integration

To integrate with Salesforce Flow:
1. Deploy this service to an accessible endpoint
2. In your Salesforce Flow, use the "HTTP Request" action to make a POST request to the `/generate_barcode_pdf` endpoint
3. Include the JSON payload with all required fields
4. Handle the PDF response in your flow

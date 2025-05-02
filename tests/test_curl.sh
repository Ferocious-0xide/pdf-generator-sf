#!/bin/bash

curl -X POST http://localhost:8080/generate_barcode_pdf \
  -H "Content-Type: application/json" \
  -d '{
    "barcodeBase64": "",
    "date": "05/01/2025",
    "service": "MJG",
    "sku": "Y",
    "jewelryType": "Ring",
    "statedWeight": 1.00,
    "statedCount": 5,
    "requestedEngraving": "kevin rulz",
    "reportNumber": "A1PBV"
  }' \
  --output test_curl_output.pdf

echo "PDF saved as test_curl_output.pdf" 
#!/bin/bash

# Base URL for your Heroku app
API_URL="https://barcode-pdf-generator-efeb33ff5fd5.herokuapp.com"

# Sample JSON payload (similar to what Salesforce would send)
JSON_PAYLOAD='{
  "reportNumber": "123456",
  "date": "2025-05-01",
  "service": "testing",
  "sku": "123uu543u",
  "jewelryType": "earrings",
  "statedWeight": "14.5 g",
  "statedCount": "2",
  "requestedEngraving": "test engraving"
}'

# Test the PDF generation endpoint
echo "Testing PDF generation endpoint..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD" \
  --output "test_barcode.pdf" \
  $API_URL/generate_barcode_pdf

echo "PDF saved as test_barcode.pdf"

# Test the image generation endpoint
echo "Testing image generation endpoint..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD" \
  --output "test_barcode.png" \
  $API_URL/generate_barcode_image

echo "Image saved as test_barcode.png"

echo "Testing complete!"
echo "You can check the resulting files to see if they contain the correct barcodes." 
import unittest
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.barcode_image_pdf import app

class TestBarcodeGenerator(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_health_endpoint(self):
        response = self.app.get('/health')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        
    def test_generate_barcode_image(self):
        test_data = {
            "reportNumber": "TEST123",
            "date": "05/01/2025",
            "service": "MJG",
            "sku": "Y",
            "jewelryType": "Ring",
            "statedWeight": "1.0",
            "statedCount": "5",
            "requestedEngraving": "Test Engraving"
        }
        response = self.app.post('/generate_barcode_image', 
                                 data=json.dumps(test_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'image/png')
        
    def test_generate_barcode_pdf(self):
        test_data = {
            "reportNumber": "TEST456",
            "date": "05/01/2025",
            "service": "MJG",
            "sku": "Y",
            "jewelryType": "Ring",
            "statedWeight": "1.0",
            "statedCount": "5",
            "requestedEngraving": "Test Engraving"
        }
        response = self.app.post('/generate_barcode_pdf', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/pdf')

if __name__ == '__main__':
    unittest.main() 
import io
import base64
import tempfile
import os
import datetime
from flask import Flask, request, send_file, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib.colors import black, white
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPM
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

# Initialize Flask app
app = Flask(__name__)

# Handle potential Heroku PostgreSQL URL format
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# Configure SQLite database (will use PostgreSQL on Heroku)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///barcode_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define model for storing barcode data
class BarcodeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(20))
    sku = db.Column(db.String(10))
    jewelry_type = db.Column(db.String(50))
    stated_weight = db.Column(db.String(20))
    stated_count = db.Column(db.String(20))
    requested_engraving = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_number': self.report_number,
            'date': self.date,
            'service': self.service,
            'sku': self.sku,
            'jewelry_type': self.jewelry_type,
            'stated_weight': self.stated_weight,
            'stated_count': self.stated_count,
            'requested_engraving': self.requested_engraving,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def create_barcode_label(data):
    # Set page dimensions (8.5 x 11 inches)
    width, height = letter
    
    # Create a BytesIO buffer for the image
    buffer = io.BytesIO()
    
    # Create a canvas object with large dimensions
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Draw border with margin
    margin = 0.5 * inch
    c.setStrokeColor(black)
    c.setLineWidth(2)
    c.rect(margin, margin, width - 2*margin, height - 2*margin)
    
    # Generate top barcode
    report_number = data.get('reportNumber', 'A1PBV')
    barcode_value = report_number
    
    # Create Code128 barcode - larger now
    barcode_width = 6 * inch
    barcode_height = 1 * inch
    barcode_x = (width - barcode_width) / 2
    barcode_y = height - margin - barcode_height - 0.5 * inch
    
    barcode_obj = code128.Code128(barcode_value, barWidth=0.012*inch, barHeight=barcode_height)
    barcode_obj.drawOn(c, barcode_x, barcode_y)
    
    # Add TS text at top right - moved inward to avoid overlapping border
    c.setFont("Helvetica-Bold", 36)
    c.drawString(width - margin - 1.0*inch, height - margin - 0.7*inch, "TS")
    
    # Add data text fields on the left side
    c.setFont("Helvetica-Bold", 18)
    text_x = 1.0 * inch
    text_y = height - 2.5 * inch
    
    # Date (bold)
    date_value = data.get('date', '05/01/2025')
    c.drawString(text_x, text_y, date_value)
    text_y -= 0.5 * inch
    
    # Switch to regular font for most fields
    c.setFont("Helvetica", 18)
    
    # Barcode number
    barcode_number = "890005108884"
    c.drawString(text_x, text_y, barcode_number)
    text_y -= 0.5 * inch
    
    # Service info
    service_text = f"Service: {data.get('service', 'MJG')}"
    c.drawString(text_x, text_y, service_text)
    text_y -= 0.5 * inch
    
    # SKU info
    sku_text = f"SKU: {data.get('sku', 'Y')}"
    c.drawString(text_x, text_y, sku_text)
    text_y -= 0.5 * inch
    
    # Jewelry Type
    jewelry_text = f"Jewelry Type: {data.get('jewelryType', 'Ring')}"
    c.drawString(text_x, text_y, jewelry_text)
    text_y -= 0.5 * inch
    
    # Stated Weight
    weight_text = f"Stated Weight: {data.get('statedWeight', '1.0')} g"
    c.drawString(text_x, text_y, weight_text)
    text_y -= 0.5 * inch
    
    # Stated Count
    count_text = f"Stated Count: {data.get('statedCount', '5')}"
    c.drawString(text_x, text_y, count_text)
    text_y -= 0.5 * inch
    
    # Requested Engraving
    c.drawString(text_x, text_y, "Requested Engraving:")
    text_y -= 0.4 * inch
    
    engraving_text = f"[{data.get('requestedEngraving', 'kevin rulz')}]"
    c.drawString(text_x, text_y, engraving_text)
    text_y -= 0.6 * inch
    
    # Report number (bold)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(text_x, text_y, report_number)
    
    # Draw table on the right
    table_width = 3 * inch
    table_height = 4 * inch
    table_x = width - margin - table_width - 0.25 * inch
    table_y = text_y + 0.5 * inch
    
    # Table data
    table_data = [
        'IMG', 'EST WT', 'PRE', 'DBL', 'QA', 'SQL', 'ENG', 'SC'
    ]
    
    # Draw table outline
    c.rect(table_x, table_y, table_width, table_height)
    
    # Draw table rows
    row_height = table_height / len(table_data)
    for i in range(1, len(table_data)):
        y = table_y + i * row_height
        c.line(table_x, y, table_x + table_width, y)
    
    # Draw vertical divider
    col_width = 2 * inch
    c.line(table_x + col_width, table_y, table_x + col_width, table_y + table_height)
    
    # Add table labels
    c.setFont("Helvetica", 14)
    for i, label in enumerate(table_data):
        y = table_y + (i + 0.5) * row_height
        c.drawString(table_x + 0.1 * inch, y - 0.1 * inch, label)
        
        # Add Y|N for the ENG row
        if label == 'ENG':
            c.drawString(table_x + col_width + 0.1 * inch, y - 0.1 * inch, "Y|N")
    
    # Draw bottom barcode
    bottom_barcode_y = 1.25 * inch
    barcode_obj.drawOn(c, barcode_x, bottom_barcode_y)
    
    # Finish the canvas and get the image
    c.save()
    buffer.seek(0)
    
    # Convert to PNG using reportlab's renderPM
    from reportlab.graphics import renderPM
    from reportlab.graphics.shapes import Drawing
    
    # Create a new Drawing for the image
    img_buffer = io.BytesIO()
    
    # Use PIL to open the PDF and convert to image
    from reportlab.lib.utils import ImageReader
    
    # For debug purposes only, save on non-Heroku environments
    if 'DYNO' not in os.environ:
        try:
            debug_dir = os.path.dirname(os.path.abspath(__file__))
            debug_file = os.path.join(debug_dir, '..', '..', 'label_debug.pdf')
            debug_file = os.path.abspath(debug_file)
            with open(debug_file, 'wb') as f:
                f.write(buffer.getvalue())
        except:
            pass
    
    # Return the PDF buffer directly instead of converting to image
    buffer.seek(0)
    return buffer

def convert_image_to_pdf(pdf_buffer):
    # The function is now redundant since create_barcode_label already returns a PDF
    # Just return the buffer
    return pdf_buffer

def save_barcode_data(data):
    """Save the barcode data to the database"""
    barcode_data = BarcodeData(
        report_number=data.get('reportNumber', ''),
        date=data.get('date', ''),
        service=data.get('service', ''),
        sku=data.get('sku', ''),
        jewelry_type=data.get('jewelryType', ''),
        stated_weight=data.get('statedWeight', ''),
        stated_count=data.get('statedCount', ''),
        requested_engraving=data.get('requestedEngraving', '')
    )
    db.session.add(barcode_data)
    db.session.commit()
    return barcode_data.id

@app.route('/', methods=['GET'])
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate_barcode_pdf', methods=['POST'])
def generate_pdf():
    try:
        # Get JSON data from request
        data = request.json
        
        # Save data to database
        barcode_id = save_barcode_data(data)
        
        # Create the PDF directly
        pdf_buffer = create_barcode_label(data)
        
        # Return the PDF as response
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'barcode_{data.get("reportNumber", "label")}.pdf'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate_barcode_image', methods=['POST'])
def generate_image():
    try:
        # Get JSON data from request
        data = request.json
        
        # Save data to database
        barcode_id = save_barcode_data(data)
        
        # Create the PDF first (now our primary format)
        pdf_buffer = create_barcode_label(data)
        
        # For the image endpoint, we'll convert the PDF to PNG using a system command
        # This is more reliable than trying to render directly
        from subprocess import Popen, PIPE
        import tempfile
        
        # Write the PDF to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            tmp_pdf.write(pdf_buffer.getvalue())
            tmp_pdf_path = tmp_pdf.name
        
        # Create a temporary file for the output PNG
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
            tmp_png_path = tmp_png.name
        
        try:
            # Try to convert using ImageMagick if available
            process = Popen(['convert', '-density', '300', tmp_pdf_path, '-quality', '100', tmp_png_path], 
                           stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            
            # Read the PNG file
            with open(tmp_png_path, 'rb') as png_file:
                img_data = png_file.read()
            
            # Clean up temporary files
            os.unlink(tmp_pdf_path)
            os.unlink(tmp_png_path)
            
            # Return the image
            img_io = io.BytesIO(img_data)
            return send_file(
                img_io,
                mimetype='image/png',
                as_attachment=True,
                download_name=f'barcode_{data.get("reportNumber", "label")}.png'
            )
        except:
            # If ImageMagick fails, fallback to returning the PDF
            os.unlink(tmp_pdf_path)
            if os.path.exists(tmp_png_path):
                os.unlink(tmp_png_path)
            
            # Just return the PDF instead
            pdf_buffer.seek(0)
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'barcode_{data.get("reportNumber", "label")}.pdf'
            )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/barcodes', methods=['GET'])
def list_barcodes():
    """Get all saved barcode data"""
    barcodes = BarcodeData.query.order_by(BarcodeData.created_at.desc()).all()
    return jsonify([barcode.to_dict() for barcode in barcodes])

@app.route('/barcodes/<int:id>', methods=['GET'])
def get_barcode(id):
    """Get a specific barcode by ID"""
    barcode = BarcodeData.query.get_or_404(id)
    return jsonify(barcode.to_dict())

@app.route('/barcodes/<int:id>/regenerate_pdf', methods=['GET'])
def regenerate_pdf(id):
    """Regenerate PDF from saved data"""
    barcode = BarcodeData.query.get_or_404(id)
    
    # Convert database model to dict that matches the expected format
    data = {
        'reportNumber': barcode.report_number,
        'date': barcode.date,
        'service': barcode.service,
        'sku': barcode.sku,
        'jewelryType': barcode.jewelry_type,
        'statedWeight': barcode.stated_weight,
        'statedCount': barcode.stated_count,
        'requestedEngraving': barcode.requested_engraving
    }
    
    # Create the PDF directly
    pdf_buffer = create_barcode_label(data)
    
    # Return the PDF
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'barcode_{barcode.report_number}.pdf'
    )

@app.route('/barcodes/<int:id>/regenerate_image', methods=['GET'])
def regenerate_image(id):
    """Regenerate image from saved data"""
    # This now follows the generate_image approach of converting the PDF
    barcode = BarcodeData.query.get_or_404(id)
    
    # Convert database model to dict that matches the expected format
    data = {
        'reportNumber': barcode.report_number,
        'date': barcode.date,
        'service': barcode.service,
        'sku': barcode.sku,
        'jewelryType': barcode.jewelry_type,
        'statedWeight': barcode.stated_weight,
        'statedCount': barcode.stated_count,
        'requestedEngraving': barcode.requested_engraving
    }
    
    # Create the PDF first
    pdf_buffer = create_barcode_label(data)
    
    # For the image endpoint, convert as in generate_image
    from subprocess import Popen, PIPE
    import tempfile
    
    # Write the PDF to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf.write(pdf_buffer.getvalue())
        tmp_pdf_path = tmp_pdf.name
    
    # Create a temporary file for the output PNG
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
        tmp_png_path = tmp_png.name
    
    try:
        # Try to convert using ImageMagick if available
        process = Popen(['convert', '-density', '300', tmp_pdf_path, '-quality', '100', tmp_png_path], 
                       stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        
        # Read the PNG file
        with open(tmp_png_path, 'rb') as png_file:
            img_data = png_file.read()
        
        # Clean up temporary files
        os.unlink(tmp_pdf_path)
        os.unlink(tmp_png_path)
        
        # Return the image
        img_io = io.BytesIO(img_data)
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'barcode_{barcode.report_number}.png'
        )
    except:
        # If ImageMagick fails, fallback to returning the PDF
        os.unlink(tmp_pdf_path)
        if os.path.exists(tmp_png_path):
            os.unlink(tmp_png_path)
        
        # Just return the PDF instead
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'barcode_{barcode.report_number}.pdf'
        )

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Use port 8080 instead of 5000 to avoid conflicts with macOS AirPlay
    app.run(debug=True, host='0.0.0.0', port=8080) 
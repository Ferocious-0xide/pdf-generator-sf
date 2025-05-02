import io
import base64
import tempfile
import os
import datetime
from flask import Flask, request, send_file, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
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
    # Set dimensions in pixels - much larger now
    width = 1800
    height = 1800
    
    # Create a new white image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts with extremely large sizes
    try:
        # For macOS/Linux
        regular_font = ImageFont.truetype("Arial", 150)
        bold_font = ImageFont.truetype("Arial-Bold", 180)
        small_font = ImageFont.truetype("Arial", 120)
    except IOError:
        try:
            # Second attempt with system fonts
            regular_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 150)
            bold_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 180)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
        except IOError:
            # Fallback to default
            regular_font = ImageFont.load_default()
            bold_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Draw border
    border_margin = 80
    draw.rectangle(
        [(border_margin, border_margin), 
         (width - border_margin, height - border_margin)], 
        outline='black', width=4
    )
    
    # Generate top barcode 
    report_number = data.get('reportNumber', 'A1PBV')
    barcode_class = barcode.get_barcode_class('code128')
    bc = barcode_class(report_number, writer=ImageWriter())
    
    # Save barcode to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        bc.write(tmp.name)
        barcode_img = Image.open(tmp.name)
        # Resize barcode to fit - much larger now
        barcode_img = barcode_img.resize((900, 200))
        # Paste top barcode
        img.paste(barcode_img, (160, 160))
        tmp_path = tmp.name
    
    # Clean up top barcode temp file
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    
    # Draw TS text at top right
    draw.text((width - 200, 180), "TS", font=bold_font, fill='black')
    
    # Left margin for text
    left_margin = 160
    
    # Draw date
    y_position = 400
    draw.text((left_margin, y_position), data.get('date', '05/01/2025'), font=bold_font, fill='black')
    
    # Draw barcode number
    y_position += 140
    draw.text((left_margin, y_position), "890005108884", font=regular_font, fill='black')
    
    # Draw service info and other fields
    y_position += 140
    draw.text((left_margin, y_position), f"Service: {data.get('service', 'MJG')}", font=regular_font, fill='black')
    
    y_position += 120
    draw.text((left_margin, y_position), f"SKU: {data.get('sku', 'Y')}", font=regular_font, fill='black')
    
    y_position += 120
    draw.text((left_margin, y_position), f"Jewelry Type: {data.get('jewelryType', 'Ring')}", font=regular_font, fill='black')
    
    y_position += 120
    draw.text((left_margin, y_position), f"Stated Weight: {data.get('statedWeight', '1.0')} g", font=regular_font, fill='black')
    
    y_position += 120
    draw.text((left_margin, y_position), f"Stated Count: {data.get('statedCount', '5')}", font=regular_font, fill='black')
    
    y_position += 120
    draw.text((left_margin, y_position), "Requested Engraving:", font=regular_font, fill='black')
    
    y_position += 80
    draw.text((left_margin, y_position), f"[{data.get('requestedEngraving', 'kevin rulz')}]", font=regular_font, fill='black')
    
    # Draw report number in bold
    y_position += 140
    draw.text((left_margin, y_position), report_number, font=bold_font, fill='black')
    
    # Generate bottom barcode
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        bc.write(tmp.name)
        barcode_img = Image.open(tmp.name)
        # Resize barcode to fit at bottom - much larger now
        barcode_img = barcode_img.resize((900, 160))
        # Paste bottom barcode
        img.paste(barcode_img, (160, height - 240))
        tmp_path = tmp.name
    
    # Clean up bottom barcode temp file
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    
    # Draw table on the right
    table_width = 500
    table_height = 800
    table_x = width - border_margin - table_width - 40
    table_y = 400
    cell_height = 100
    
    # Table data
    table_data = [
        'IMG', 'EST WT', 'PRE', 'DBL', 'QA', 'SQL', 'ENG', 'SC'
    ]
    
    # Draw table grid
    draw.rectangle(
        [(table_x, table_y), 
         (table_x + table_width, table_y + table_height)], 
        outline='black', width=2
    )
    
    # Draw horizontal lines
    for i in range(1, len(table_data)):
        y = table_y + i * cell_height
        draw.line([(table_x, y), (table_x + table_width, y)], fill='black', width=2)
    
    # Draw vertical divider
    col_width = 300
    draw.line(
        [(table_x + col_width, table_y), 
         (table_x + col_width, table_y + table_height)], 
        fill='black', width=2
    )
    
    # Add table labels
    for i, label in enumerate(table_data):
        y = table_y + i * cell_height + 30
        draw.text((table_x + 20, y), label, font=small_font, fill='black')
        
        # Add Y|N for the ENG row
        if label == 'ENG':
            draw.text((table_x + col_width + 20, y), "Y|N", font=small_font, fill='black')
    
    # Save a local copy for debugging only if not on Heroku
    if 'DYNO' not in os.environ:
        debug_dir = os.path.dirname(os.path.abspath(__file__))
        debug_file = os.path.join(debug_dir, '..', '..', 'label_debug.png')
        debug_file = os.path.abspath(debug_file)
        img.save(debug_file)
    
    return img

def convert_image_to_pdf(image):
    # Create a BytesIO buffer for the PDF
    buffer = io.BytesIO()
    
    # Set PDF size to letter size (8.5x11 inches) - standard size
    page_size = (8.5*inch, 11*inch)
    
    # Create a canvas with larger page size
    c = canvas.Canvas(buffer, pagesize=page_size)
    
    # Convert PIL Image to a format ReportLab can use
    img_data = io.BytesIO()
    image.save(img_data, format='PNG')
    img_data.seek(0)
    img_reader = ImageReader(img_data)
    
    # Center the image on the page with margins
    margin = 0.5 * inch
    image_width = page_size[0] - 2 * margin
    image_height = image_width  # Keep it square
    
    # Calculate y position to center vertically
    y_position = (page_size[1] - image_height) / 2
    
    # Draw the image on the PDF, scaling it to fill most of the page
    c.drawImage(img_reader, margin, y_position, width=image_width, height=image_height)
    
    # Save the PDF
    c.save()
    buffer.seek(0)
    return buffer

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
        
        # Create the image
        label_image = create_barcode_label(data)
        
        # Convert to PDF
        pdf_buffer = convert_image_to_pdf(label_image)
        
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
        
        # Create the image
        label_image = create_barcode_label(data)
        
        # Convert to bytes
        img_io = io.BytesIO()
        label_image.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Return the image
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'barcode_{data.get("reportNumber", "label")}.png'
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
    
    # Create the image and PDF
    label_image = create_barcode_label(data)
    pdf_buffer = convert_image_to_pdf(label_image)
    
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
    
    # Create the image
    label_image = create_barcode_label(data)
    
    # Convert to bytes
    img_io = io.BytesIO()
    label_image.save(img_io, 'PNG')
    img_io.seek(0)
    
    # Return the image
    return send_file(
        img_io,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'barcode_{barcode.report_number}.png'
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
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
    # Set dimensions in pixels (very large)
    width = 2000 
    height = 2000
    
    # Create a new white image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Use PIL's default font - it's small but guaranteed to work
    default_font = ImageFont.load_default()
    
    # Draw border
    border_margin = 50
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
        # Resize barcode to fit
        barcode_img = barcode_img.resize((1200, 300))
        # Paste top barcode
        img.paste(barcode_img, (400, 150))
        tmp_path = tmp.name
    
    # Clean up top barcode temp file
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    
    # Draw TS text at top right
    ts_text = "TS"
    # Create a separate image for TS text
    ts_img = Image.new('RGB', (200, 200), color='white')
    ts_draw = ImageDraw.Draw(ts_img)
    # Use a much larger font size by creating a larger canvas
    font_size = 80
    ts_draw.text((50, 60), ts_text, font=default_font, fill='black')
    # Resize to make it appear larger
    ts_img = ts_img.resize((200, 200), Image.LANCZOS)
    # Paste onto main image
    img.paste(ts_img, (width - 250, 150))
    
    # Create a function to draw enlarged text
    def draw_large_text(text, position, is_bold=False):
        # Create temporary image for text at high resolution
        text_img_width = len(text) * 80
        text_img_height = 150
        text_img = Image.new('RGB', (text_img_width, text_img_height), color='white')
        text_draw = ImageDraw.Draw(text_img)
        
        # Draw text multiple times with slight offsets for bold effect if needed
        if is_bold:
            for offset in range(-2, 3):
                text_draw.text((40 + offset, 40), text, font=default_font, fill='black')
                text_draw.text((40, 40 + offset), text, font=default_font, fill='black')
        else:
            text_draw.text((40, 40), text, font=default_font, fill='black')
        
        # Scale up to make text appear larger
        text_img = text_img.resize((text_img_width, text_img_height), Image.LANCZOS)
        img.paste(text_img, position)
        return position[1] + text_img_height + 20
    
    # Define text content
    left_margin = 150
    y_pos = 500
    
    # Draw all text fields with large text
    date_text = data.get('date', '05/01/2025')
    y_pos = draw_large_text(date_text, (left_margin, y_pos), is_bold=True)
    
    barcode_number = "890005108884"
    y_pos = draw_large_text(barcode_number, (left_margin, y_pos))
    
    service_text = f"Service: {data.get('service', 'MJG')}"
    y_pos = draw_large_text(service_text, (left_margin, y_pos))
    
    sku_text = f"SKU: {data.get('sku', 'Y')}"
    y_pos = draw_large_text(sku_text, (left_margin, y_pos))
    
    jewelry_text = f"Jewelry Type: {data.get('jewelryType', 'Ring')}"
    y_pos = draw_large_text(jewelry_text, (left_margin, y_pos))
    
    weight_text = f"Stated Weight: {data.get('statedWeight', '1.0')} g"
    y_pos = draw_large_text(weight_text, (left_margin, y_pos))
    
    count_text = f"Stated Count: {data.get('statedCount', '5')}"
    y_pos = draw_large_text(count_text, (left_margin, y_pos))
    
    engraving_label = "Requested Engraving:"
    y_pos = draw_large_text(engraving_label, (left_margin, y_pos))
    
    engraving_text = f"[{data.get('requestedEngraving', 'kevin rulz')}]"
    y_pos = draw_large_text(engraving_text, (left_margin, y_pos))
    
    # Draw report number at the bottom
    y_pos = draw_large_text(report_number, (left_margin, y_pos), is_bold=True)
    
    # Generate bottom barcode
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        bc.write(tmp.name)
        barcode_img = Image.open(tmp.name)
        # Resize barcode to fit at bottom
        barcode_img = barcode_img.resize((1200, 300))
        # Paste bottom barcode
        img.paste(barcode_img, (400, height - 400))
        tmp_path = tmp.name
    
    # Clean up bottom barcode temp file
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    
    # Draw table on the right
    table_width = 500
    table_height = 800
    table_x = width - border_margin - table_width - 50
    table_y = 500
    cell_height = 100
    
    # Table data
    table_data = [
        'IMG', 'EST WT', 'PRE', 'DBL', 'QA', 'SQL', 'ENG', 'SC'
    ]
    
    # Draw table grid
    draw.rectangle(
        [(table_x, table_y), 
         (table_x + table_width, table_y + table_height)], 
        outline='black', width=3
    )
    
    # Draw horizontal lines
    for i in range(1, len(table_data)):
        y = table_y + i * cell_height
        draw.line([(table_x, y), (table_x + table_width, y)], fill='black', width=3)
    
    # Draw vertical divider
    col_width = 350
    draw.line(
        [(table_x + col_width, table_y), 
         (table_x + col_width, table_y + table_height)], 
        fill='black', width=3
    )
    
    # Add table labels using the large text technique
    for i, label in enumerate(table_data):
        y = table_y + i * cell_height + 30
        
        # Create temporary image for text
        label_img_width = 300
        label_img_height = 60
        label_img = Image.new('RGB', (label_img_width, label_img_height), color='white')
        label_draw = ImageDraw.Draw(label_img)
        
        # Draw the label text
        label_draw.text((20, 15), label, font=default_font, fill='black')
        
        # Scale up for visibility
        label_img = label_img.resize((label_img_width, label_img_height), Image.LANCZOS)
        img.paste(label_img, (table_x + 20, y))
        
        # Add Y|N for the ENG row
        if label == 'ENG':
            yn_img = Image.new('RGB', (100, 60), color='white')
            yn_draw = ImageDraw.Draw(yn_img)
            yn_draw.text((20, 15), "Y|N", font=default_font, fill='black')
            yn_img = yn_img.resize((100, 60), Image.LANCZOS)
            img.paste(yn_img, (table_x + col_width + 50, y))
    
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
    
    # Use a larger PDF page size
    page_size = (8.5*inch, 11*inch)
    
    # Create the canvas
    c = canvas.Canvas(buffer, pagesize=page_size)
    
    # Convert PIL Image to a format ReportLab can use
    img_data = io.BytesIO()
    image.save(img_data, format='PNG')
    img_data.seek(0)
    img_reader = ImageReader(img_data)
    
    # Minimize margins to make the image as large as possible
    margin = 0.25 * inch
    image_width = page_size[0] - 2 * margin
    image_height = image_width  # Keep it square
    
    # Center the image on the page
    y_position = (page_size[1] - image_height) / 2
    
    # Draw the image on the PDF with maximum size
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
import io
import base64
import tempfile
import os
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from reportlab.lib.utils import ImageReader

app = Flask(__name__)

def create_barcode_label(data):
    # Set dimensions in pixels (3 inches at 300 DPI)
    width = 900
    height = 900
    
    # Create a new white image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts (fallback to default if not available)
    try:
        # For macOS/Linux
        regular_font = ImageFont.truetype("Arial", 30)
        bold_font = ImageFont.truetype("Arial-Bold", 36)
        small_font = ImageFont.truetype("Arial", 20)
    except IOError:
        try:
            # Second attempt with system fonts
            regular_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
            bold_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except IOError:
            # Fallback to default
            regular_font = ImageFont.load_default()
            bold_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Draw border
    border_margin = 40
    draw.rectangle(
        [(border_margin, border_margin), 
         (width - border_margin, height - border_margin)], 
        outline='black', width=2
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
        barcode_img = barcode_img.resize((450, 100))
        # Paste top barcode
        img.paste(barcode_img, (80, 80))
        tmp_path = tmp.name
    
    # Clean up top barcode temp file
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    
    # Draw TS text at top right
    draw.text((width - 100, 90), "TS", font=bold_font, fill='black')
    
    # Left margin for text
    left_margin = 80
    
    # Draw date
    y_position = 200
    draw.text((left_margin, y_position), data.get('date', '05/01/2025'), font=bold_font, fill='black')
    
    # Draw barcode number
    y_position += 70
    draw.text((left_margin, y_position), "890005108884", font=regular_font, fill='black')
    
    # Draw service info and other fields
    y_position += 70
    draw.text((left_margin, y_position), f"Service: {data.get('service', 'MJG')}", font=regular_font, fill='black')
    
    y_position += 60
    draw.text((left_margin, y_position), f"SKU: {data.get('sku', 'Y')}", font=regular_font, fill='black')
    
    y_position += 60
    draw.text((left_margin, y_position), f"Jewelry Type: {data.get('jewelryType', 'Ring')}", font=regular_font, fill='black')
    
    y_position += 60
    draw.text((left_margin, y_position), f"Stated Weight: {data.get('statedWeight', '1.0')} g", font=regular_font, fill='black')
    
    y_position += 60
    draw.text((left_margin, y_position), f"Stated Count: {data.get('statedCount', '5')}", font=regular_font, fill='black')
    
    y_position += 60
    draw.text((left_margin, y_position), "Requested Engraving:", font=regular_font, fill='black')
    
    y_position += 40
    draw.text((left_margin, y_position), f"[{data.get('requestedEngraving', 'kevin rulz')}]", font=regular_font, fill='black')
    
    # Draw report number in bold
    y_position += 70
    draw.text((left_margin, y_position), report_number, font=bold_font, fill='black')
    
    # Generate bottom barcode
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        bc.write(tmp.name)
        barcode_img = Image.open(tmp.name)
        # Resize barcode to fit at bottom
        barcode_img = barcode_img.resize((450, 80))
        # Paste bottom barcode
        img.paste(barcode_img, (80, height - 120))
        tmp_path = tmp.name
    
    # Clean up bottom barcode temp file
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    
    # Draw table on the right
    table_width = 250
    table_height = 400
    table_x = width - border_margin - table_width - 20
    table_y = 200
    cell_height = 50
    
    # Table data
    table_data = [
        'IMG', 'EST WT', 'PRE', 'DBL', 'QA', 'SQL', 'ENG', 'SC'
    ]
    
    # Draw table grid
    draw.rectangle(
        [(table_x, table_y), 
         (table_x + table_width, table_y + table_height)], 
        outline='black', width=1
    )
    
    # Draw horizontal lines
    for i in range(1, len(table_data)):
        y = table_y + i * cell_height
        draw.line([(table_x, y), (table_x + table_width, y)], fill='black', width=1)
    
    # Draw vertical divider
    col_width = 150
    draw.line(
        [(table_x + col_width, table_y), 
         (table_x + col_width, table_y + table_height)], 
        fill='black', width=1
    )
    
    # Add table labels
    for i, label in enumerate(table_data):
        y = table_y + i * cell_height + 15
        draw.text((table_x + 10, y), label, font=small_font, fill='black')
        
        # Add Y|N for the ENG row
        if label == 'ENG':
            draw.text((table_x + col_width + 10, y), "Y|N", font=small_font, fill='black')
    
    # Save a local copy for debugging
    debug_dir = os.path.dirname(os.path.abspath(__file__))
    debug_file = os.path.join(debug_dir, '..', '..', 'label_debug.png')
    debug_file = os.path.abspath(debug_file)
    img.save(debug_file)
    
    return img

def convert_image_to_pdf(image):
    # Create a BytesIO buffer for the PDF
    buffer = io.BytesIO()
    
    # Create a canvas with 3x3 inch size
    c = canvas.Canvas(buffer, pagesize=(3*inch, 3*inch))
    
    # Convert PIL Image to a format ReportLab can use
    img_data = io.BytesIO()
    image.save(img_data, format='PNG')
    img_data.seek(0)
    img_reader = ImageReader(img_data)
    
    # Draw the image on the PDF
    c.drawImage(img_reader, 0, 0, width=3*inch, height=3*inch)
    
    # Save the PDF
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/generate_barcode_pdf', methods=['POST'])
def generate_pdf():
    try:
        # Get JSON data from request
        data = request.json
        
        # Create the image
        label_image = create_barcode_label(data)
        
        # Convert to PDF
        pdf_buffer = convert_image_to_pdf(label_image)
        
        # Return the PDF as response
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='barcode.pdf'
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
            download_name='barcode.png'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Use port 8080 instead of 5000 to avoid conflicts with macOS AirPlay
    app.run(debug=True, host='0.0.0.0', port=8080) 
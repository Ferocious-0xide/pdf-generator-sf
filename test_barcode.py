import base64
import io
from PIL import Image
try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

# The base64 encoded barcode image
base64_data = "iVBORw0KGgoAAAANSUhEUgAAAZkAAACCAQAAAAC8uIiPAAAACXBIWXMAABcSAAAXEgFnn9JSAAAAEnRFWHRTb2Z0d2FyZQBCYXJjb2RlNEryjnYuAAABvklEQVR4Xu3TsWrcMBzHcV09eClRujUQ0JAX6JgsUR+l0CFzt06VoYOXgNcMgXuUOnhwh9Jn8KFCVx1ZdFTVr38lV2hlhTiFbn9tB9+POekvCSDqV6dH1fq6v5Rf37yewsWJrq4Oz/zR5z48/3Zhq2e1Pj17qa6Puy8HBwZoBCNGjBgxYsSIESNGjBgxYsSIESNGjBgxYv9N/TkxWi/ZijKuMJkMARhQj0J08DprJshJz2FCh8JuYqQML3MmiLSjbxDE6EP9KvOmhm67XZBr2ucBIObH/DhXLVj1swQOkSFMSbUgpBR0mZJCSGht/doS0jdZslDKCTU7dE2Sx5C3hKiU9ssRbSnbmfDCscKNp7rZUg7tbVB4LCGhTBykyUlFIzTlpAWFQY0aG+ypIS8cfK7/el1PdAx0nBXWVJCDmhHS1uj/zXScPsXWVJCtIWho4GmY+u8ke5dlpTQANhGmD26/8tfq4TaP5BMaMk1kr/ReguV0JAlBUSzpSwdRLchZOQSFDR0C7vzehyiotP79Oh7cuK9UIKuAr3Fvoo6CNU8/nLvkEwIUx11Gq7KmjLqNd3UCl7RVW/Qm6yZoSXr39AvKgBwgEJ01wkAAAAASUVORK5CYII="

# Fix padding if needed
base64_data += '=' * (-len(base64_data) % 4)

# Decode base64 and create an image
image_data = base64.b64decode(base64_data)
image = Image.open(io.BytesIO(image_data))

# Save the image
image.save("decoded_barcode.png")
print(f"Saved image to decoded_barcode.png")

# Try to read the barcode
if PYZBAR_AVAILABLE:
    barcodes = decode(image)
    if barcodes:
        for barcode in barcodes:
            barcode_type = barcode.type
            barcode_data = barcode.data.decode('utf-8')
            print(f"Barcode Type: {barcode_type}")
            print(f"Barcode Data: {barcode_data}")
    else:
        print("No barcode detected in the image")
else:
    print("To read the barcode, install the pyzbar library:")
    print("pip install pyzbar")
    print("Then run this script again.")

print("\nYou can also test this barcode with:")
print("1. Online barcode scanner: https://online-barcode-reader.inliteresearch.com/")
print("2. Mobile barcode scanner app")
print("3. Hardware barcode scanner") 
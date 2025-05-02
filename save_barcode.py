import base64

# The base64 encoded barcode image
base64_data = "iVBORw0KGgoAAAANSUhEUgAAAZkAAACCAQAAAAC8uIiPAAAACXBIWXMAABcSAAAXEgFnn9JSAAAAEnRFWHRTb2Z0d2FyZQBCYXJjb2RlNEryjnYuAAABvklEQVR4Xu3TsWrcMBzHcV09eClRujUQ0JAX6JgsUR+l0CFzt06VoYOXgNcMgXuUOnhwh9Jn8KFCVx1ZdFTVr38lV2hlhTiFbn9tB9+POekvCSDqV6dH1fq6v5Rf37yewsWJrq4Oz/zR5z48/3Zhq2e1Pj17qa6Puy8HBwZoBCNGjBgxYsSIESNGjBgxYsSIESNGjBgxYv9N/TkxWi/ZijKuMJkMARhQj0J08DprJshJz2FCh8JuYqQML3MmiLSjbxDE6EP9KvOmhm67XZBr2ucBIObH/DhXLVj1swQOkSFMSbUgpBR0mZJCSGht/doS0jdZslDKCTU7dE2Sx5C3hKiU9ssRbSnbmfDCscKNp7rZUg7tbVB4LCGhTBykyUlFIzTlpAWFQY0aG+ypIS8cfK7/el1PdAx0nBXWVJCDmhHS1uj/zXScPsXWVJCtIWho4GmY+u8ke5dlpTQANhGmD26/8tfq4TaP5BMaMk1kr/ReguV0JAlBUSzpSwdRLchZOQSFDR0C7vzehyiotP79Oh7cuK9UIKuAr3Fvoo6CNU8/nLvkEwIUx11Gq7KmjLqNd3UCl7RVW/Qm6yZoSXr39AvKgBwgEJ01wkAAAAASUVORK5CYII="

# Fix padding if needed
base64_data += '=' * (-len(base64_data) % 4)

# Decode base64 and create a binary file
binary_data = base64.b64decode(base64_data)

# Save directly as PNG file
with open("barcode.png", "wb") as f:
    f.write(binary_data)

print(f"Saved barcode image to barcode.png")
print("You can open this file with any image viewer")
print("\nTo scan this barcode, you can use:")
print("1. A mobile phone with a barcode scanner app")
print("2. An online barcode reader service")
print("3. A hardware barcode scanner") 
import qrcode

# URL that users will scan (change this to your project's base URL)
qr_url = "https://hr.mediusware.xyz/scan/"

# Create the QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(qr_url)
qr.make(fit=True)

# Save the QR code as an image
img = qr.make_image(fill='black', back_color='white')

# Save it to your static files directory or any directory of choice
img.save("static/static_qr_code.png")

import qrcode
from PIL import Image

qr_url = "https://hr.mediusware.xyz/scan/"

# Create the QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,  
    box_size=10,
    border=4,
)
qr.add_data(qr_url)
qr.make(fit=True)

qr_img = qr.make_image(fill='black', back_color='white').convert('RGB')

logo = Image.open("static/stationary/mw-logo.png")

qr_width, qr_height = qr_img.size
logo_size = int(qr_width * 0.5)  
logo_aspect_ratio = logo.width / logo.height  

new_logo_size = (logo_size, int(logo_size / logo_aspect_ratio))
logo = logo.resize(new_logo_size)

background = Image.new('RGB', logo.size, 'white')

background.paste(logo, (0, 0), logo) 

logo_width, logo_height = background.size
logo_pos = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)

qr_img.paste(background, logo_pos)

qr_img.save("static/static_qr_code_with_logo.png")

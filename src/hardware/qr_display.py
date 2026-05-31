import logging
import qrcode
from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)

def generate_qr_image(ssid: str, passwd: str, mac: str = "", rssi: str = "", width: int = 250, height: int = 122) -> Image.Image:
    """
    Generates a PIL Image containing the WiFi QR Code and credentials.
    Designed for the Waveshare 2.13" E-Ink (250x122).
    """
    try:
        # 1. Create a blank white canvas
        img = Image.new("1", (width, height), color=1)  # 1-bit color (white background)
        d = ImageDraw.Draw(img)
        
        # 2. Generate the WiFi QR Code
        wifi_data = f"WIFI:T:WPA;S:{ssid};P:{passwd};;"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=2,
        )
        qr.add_data(wifi_data)
        qr.make(fit=True)
        qimg = qr.make_image(fill_color="black", back_color="white").convert("1")
        
        # 3. Paste the QR code onto the left side of the canvas
        img.paste(qimg, (0, 0))
        
        # 4. Draw text on the right side
        text_x = qimg.width + 5
        
        # Try to load fonts, fallback to default
        try:
            from config import PROJECT_DIR
            font_path = str(PROJECT_DIR / "assets" / "DejaVuSansMono-Bold.ttf")
            f_title = ImageFont.truetype(font_path, 12)
            f_body = ImageFont.truetype(font_path, 14)
        except Exception:
            f_title = ImageFont.load_default()
            f_body = ImageFont.load_default()
            
        y = 5
        d.text((text_x, y), "SSID:", font=f_title, fill=0)
        y += 15
        d.text((text_x, y), ssid[:15], font=f_body, fill=0)  # truncate long ssids
        
        y += 20
        d.text((text_x, y), "PASSWORD:", font=f_title, fill=0)
        y += 15
        d.text((text_x, y), passwd[:15], font=f_body, fill=0)
        
        if rssi:
            y += 25
            d.text((text_x, y), f"RSSI: {rssi}dBm", font=f_title, fill=0)
            
        return img
    except Exception as e:
        log.error(f"Failed to generate QR Image: {e}")
        # Fallback error image
        img = Image.new("1", (width, height), color=1)
        ImageDraw.Draw(img).text((10, 50), "QR Gen Error", fill=0)
        return img

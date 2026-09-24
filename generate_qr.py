import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import qrcode
import socket
import os

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

ip = get_local_ip()
url = f"http://{ip}:5000"

qr_path = r"C:\Users\Lucru\Desktop\interconti\Scaneaza_pe_Telefon.png"
img = qrcode.make(url)
img.save(qr_path)

print(f"URL: {url}")
print(f"QR code salvat: {qr_path}")

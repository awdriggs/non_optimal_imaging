# share.py

import http.server
import socketserver
import socket
from pathlib import Path
import os

httpd = None

# === Base directories ===
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CAPTURES_DIR = FRONTEND_DIR / "captures"

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve images from Captures/, frontend files otherwise
        if path.endswith('.jpg') or path.endswith('.jpeg') or path.endswith('.png'):
            full_path = CAPTURES_DIR / path.lstrip('/')
        else:
            full_path = FRONTEND_DIR / path.lstrip('/')

        return str(full_path)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

def start_server(port=8000):
    global httpd

    os.chdir(FRONTEND_DIR)  # Set working directory to serve from frontend

    handler = CustomHandler
    httpd = ReusableTCPServer(("", port), handler)

    print(f"🌐 Serving at http://{get_ip_address()}:{port}")
    httpd.serve_forever()

def stop_server():
    global httpd
    if httpd:
        httpd.shutdown()
        httpd = None
        print("🛑 Server stopped.")


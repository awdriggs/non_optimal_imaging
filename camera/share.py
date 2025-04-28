# share.py

import http.server
import socketserver
import socket
import os
import json
from pathlib import Path

httpd = None

# === Base directories ===
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CAPTURES_DIR = FRONTEND_DIR / "captures"

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/images":
            self.list_images_api()
        else:
            super().do_GET()

    def list_images_api(self):
        try:
            # List all image files in /captures
            image_files = [
                f.name for f in CAPTURES_DIR.iterdir()
                if f.suffix.lower() in [".jpg", ".jpeg", ".png"]
            ]

            # Sort newest first
            image_files.sort(reverse=True)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(image_files).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def translate_path(self, path):
        if path.startswith("/captures/"):
            return str(CAPTURES_DIR / path[len("/captures/"):])
        else:
            return str(FRONTEND_DIR / path.lstrip("/"))

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

    os.chdir(FRONTEND_DIR)  # Serve from frontend

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


import http.server
import socketserver
import os
import socket
import json

httpd = None

# === Base directories ===
BASE_DIR = '/home/awdriggs/frontend'
CAPTURES_DIR = '/home/awdriggs/frontend/captures'

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith('/Captures/'):
            # Serve images from Captures folder
            return os.path.join(CAPTURES_DIR, path[len('/Captures/'):])
        else:
            # Serve frontend files normally
            return os.path.join(BASE_DIR, path.lstrip('/'))

    def do_GET(self):
        if self.path == '/images/':
            # Return JSON list of images from Captures
            image_list = [f for f in os.listdir(CAPTURES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            image_list.sort()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(image_list).encode())
        else:
            # Default serving
            super().do_GET()

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
    os.chdir(BASE_DIR)  # Serve from /frontend by default
    handler = CustomHandler
    httpd = ReusableTCPServer(("", port), handler)
    print(f"Serving at http://{get_ip_address()}:{port}")
    httpd.serve_forever()

def stop_server():
    global httpd
    if httpd:
        httpd.shutdown()
        httpd = None
        print("Server stopped.")


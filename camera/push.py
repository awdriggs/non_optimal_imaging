# camera/push.py
import requests
from pathlib import Path
import threading

# --- Configuration ---
# This is the address of your Pi 4 server.
# Using .local requires Avahi/Bonjour to be working on your network.
# If it fails, you may need to use the Pi 4's IP address directly.
SERVER_URL = "http://nonopserver.local:3000/api/upload"

def send_image_to_server(image_path: Path, camera_id: str):

    def _send():
        print(f"📡 Attempting to push {image_path.name} to server for camera '{camera_id}'...")
        
        
        try:
            # We need to open the file in binary read mode ('rb')
            with open(image_path, 'rb') as f:
                # The files dictionary key 'photo' must match what the server's
                # multer middleware expects. The data dictionary key 'cameraId'
                # must also match.
                files = {'photo': (image_path.name, f, 'image/jpeg')}
                data = {'cameraId': camera_id}

                # Send the request with a timeout. If the server doesn't respond
                # in 5 seconds, it will raise a Timeout exception.
                response = requests.post(SERVER_URL, files=files, data=data, timeout=5)

                # Check if the server responded with a success code (e.g., 200 OK)
                if response.status_code == 200:
                    print(f"✅ Successfully pushed {image_path.name} to server.")
                else:
                    print(f"⚠️ Server returned an error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            # This is a robust catch-all for any network-related error:
            # - ConnectionError (server is down, DNS failed)
            # - Timeout (server is slow or unresponsive)
            # - etc.
            print(f"❌ Failed to connect to the server: {e}")
            print("   The image is saved locally, but was not sent.")

    threading.Thread(target=_send, daemon=True).start()

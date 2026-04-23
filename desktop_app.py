import webview
import threading
import time
import os
from server import app

def run_server():
    # Turn off the reloader so it doesn't try to spawn multiple threads
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Start the Flask server in a background daemon thread
    flask_thread = threading.Thread(target=run_server)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Optional: wait a moment for the server to spin up
    time.sleep(1)
    
    # Create the PyWebView Window pointing to the local Flask server
    window = webview.create_window(
        title='TrustNTrack - Instagram Comment Moderation',
        url='http://127.0.0.1:5000',
        width=1100,
        height=800,
        min_size=(900, 650)
    )
    
    # Start the GUI
    webview.start()

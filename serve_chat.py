#!/usr/bin/env python3
"""
Simple HTTP server to serve the chat widget
"""

import http.server
import socketserver
import webbrowser
import os

PORT = 8080

class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/chat':
            self.path = '/chat-widget.html'
        return super().do_GET()

def main():
    os.chdir('/app')
    
    with socketserver.TCPServer(("", PORT), ChatHandler) as httpd:
        print(f"🚀 Chat widget server running at http://localhost:{PORT}")
        print(f"📱 Open http://localhost:{PORT} to test the chat")
        print("Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
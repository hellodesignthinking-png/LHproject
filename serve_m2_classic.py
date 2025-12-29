#!/usr/bin/env python3
"""
Simple HTTP server to view M2 Classic Appraisal Report
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class M2ClassicHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/m2-classic':
            self.path = '/generated_reports/M2_Classic_Format_Updated.html'
        return super().do_GET()

if __name__ == '__main__':
    os.chdir('/home/user/webapp')
    port = 8092
    server = HTTPServer(('0.0.0.0', port), M2ClassicHandler)
    print(f"✅ M2 Classic Report Server")
    print(f"🌐 Server: http://localhost:{port}/m2-classic")
    print(f"📊 Serving: M2_Classic_Format_Updated.html")
    print(f"\nPress Ctrl+C to stop")
    server.serve_forever()

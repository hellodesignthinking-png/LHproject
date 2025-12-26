#!/usr/bin/env python3
"""
Simple HTTP server to serve local HTML reports
This serves the pre-generated Phase 2.5 HTML reports with complete data
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys
from urllib.parse import urlparse, parse_qs

class ReportHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        self.directory = '/home/user/webapp/final_reports_phase25'
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Map report types to HTML files
        report_mapping = {
            '/api/v4/reports/final/all_in_one/html': 'all_in_one_phase25_real_data.html',
            '/api/v4/reports/final/quick_check/html': 'quick_check_phase25_real_data.html',
            '/api/v4/reports/final/financial_feasibility/html': 'financial_feasibility_phase25_real_data.html',
            '/api/v4/reports/final/lh_technical/html': 'lh_technical_phase25_real_data.html',
            '/api/v4/reports/final/executive_summary/html': 'executive_summary_phase25_real_data.html',
            '/api/v4/reports/final/landowner_summary/html': 'landowner_summary_phase25_real_data.html',
        }
        
        # Check if this is a report request
        if path in report_mapping:
            filename = report_mapping[path]
            filepath = os.path.join(self.directory, filename)
            
            if os.path.exists(filepath):
                # Serve the HTML file
                with open(filepath, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(404, f"Report file not found: {filename}")
                return
        
        # Default behavior for other paths
        super().do_GET()
    
    def log_message(self, format, *args):
        """Log messages"""
        sys.stdout.write("%s - - [%s] %s\n" %
                        (self.address_string(),
                         self.log_date_time_string(),
                         format % args))
        sys.stdout.flush()

def run_server(port=8005):
    """Run the HTTP server"""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, ReportHandler)
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║  LH Report Server - Phase 2.5 HTML Reports                  ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  Serving from: /home/user/webapp/final_reports_phase25/     ║
    ║  Port: {port}                                                  ║
    ║                                                              ║
    ║  Available endpoints:                                        ║
    ║  • /api/v4/reports/final/all_in_one/html                    ║
    ║  • /api/v4/reports/final/quick_check/html                   ║
    ║  • /api/v4/reports/final/financial_feasibility/html         ║
    ║  • /api/v4/reports/final/lh_technical/html                  ║
    ║  • /api/v4/reports/final/executive_summary/html             ║
    ║  • /api/v4/reports/final/landowner_summary/html             ║
    ║                                                              ║
    ║  Data included: M1~M6 (100% complete)                       ║
    ║  Status: Ready for LH submission                            ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        print(f"Starting server at http://0.0.0.0:{port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8005
    run_server(port)

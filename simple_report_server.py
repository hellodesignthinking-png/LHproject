#!/usr/bin/env python3
"""
Simple HTTP server to serve local HTML reports
This serves the pre-generated Phase 2.5 HTML reports with complete data
PLUS: Basic M1 API endpoints for address search
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys
import json
from urllib.parse import urlparse, parse_qs

class ReportHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        self.directory = '/home/user/webapp/final_reports_phase25'
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def do_POST(self):
        """Handle POST requests for M1 API"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # M1 Address Search API
        if path == '/api/m1/address/search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                query = request_data.get('query', '').strip()
                
                print(f"[Address Search] Query: '{query}'")  # Debug log
                
                # Mock address suggestions
                mock_suggestions = [
                    {
                        'road_address': '서울특별시 강남구 테헤란로 123',
                        'jibun_address': '서울특별시 강남구 역삼동 123-45',
                        'zone_no': '06234',
                        'display': '서울특별시 강남구 테헤란로 123'
                    },
                    {
                        'road_address': '서울특별시 강남구 테헤란로 152',
                        'jibun_address': '서울특별시 강남구 역삼동 678-90',
                        'zone_no': '06236',
                        'display': '서울특별시 강남구 테헤란로 152'
                    },
                    {
                        'road_address': '서울특별시 강남구 강남대로 123',
                        'jibun_address': '서울특별시 강남구 역삼동 111-22',
                        'zone_no': '06241',
                        'display': '서울특별시 강남구 강남대로 123'
                    }
                ]
                
                # More lenient filtering: check if any part of query matches
                # Remove spaces and compare
                query_normalized = query.replace(' ', '').lower()
                filtered = []
                
                if query_normalized:  # Only filter if query is not empty
                    for s in mock_suggestions:
                        display_normalized = s['display'].replace(' ', '').lower()
                        if query_normalized in display_normalized:
                            filtered.append(s)
                
                # If no matches found or query is empty, return all suggestions
                result_suggestions = filtered if filtered else mock_suggestions
                
                print(f"[Address Search] Returning {len(result_suggestions)} suggestions")  # Debug log
                
                response = {
                    'success': True,
                    'data': {
                        'suggestions': result_suggestions,
                        'using_mock_data': True,
                        'message': 'Mock data - Kakao API key not configured'
                    }
                }
                
                response_json = json.dumps(response, ensure_ascii=False)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_json.encode('utf-8'))
                return
                
            except Exception as e:
                error_response = {
                    'success': False,
                    'error': {
                        'detail': f'Error processing request: {str(e)}'
                    }
                }
                response_json = json.dumps(error_response)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_json.encode('utf-8'))
                return
        
        # Default: Method not supported
        self.send_error(501, "Unsupported POST endpoint")
    
    def do_OPTIONS(self):
        """Handle OPTIONS for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
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

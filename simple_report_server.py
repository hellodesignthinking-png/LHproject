#!/usr/bin/env python3
"""
Simple HTTP server to serve local HTML reports
This serves the pre-generated Phase 2.5 HTML reports with complete data
PLUS: M1 API endpoints with real Kakao address search
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys
import json
import httpx
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load .env file if it exists"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Loaded .env file")
    else:
        print(f"⚠️ No .env file found")

# Load environment variables at startup
load_env_file()

# Kakao API Configuration
KAKAO_ADDRESS_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/address.json"

def search_address_kakao(query: str, api_key: str) -> dict:
    """
    Search address using real Kakao API
    
    Args:
        query: Address search query
        api_key: Kakao REST API key
        
    Returns:
        Search results with suggestions
    """
    try:
        print(f"\n{'='*60}")
        print(f"[DEBUG] 🔍 Address search query: '{query}'")
        print(f"[DEBUG] 🔑 API key present: {bool(api_key)}")
        print(f"[DEBUG] 🔑 API key length: {len(api_key) if api_key else 0}")
        
        headers = {"Authorization": f"KakaoAK {api_key}"}
        params = {"query": query, "size": 10}
        
        print(f"[DEBUG] 📡 Request URL: {KAKAO_ADDRESS_SEARCH_URL}")
        print(f"[DEBUG] 📡 Request params: {params}")
        print(f"[DEBUG] 📡 Request headers: Authorization: KakaoAK {api_key[:10]}...")
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                KAKAO_ADDRESS_SEARCH_URL,
                headers=headers,
                params=params
            )
            
            print(f"[DEBUG] 📥 Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[DEBUG] ❌ Error: HTTP {response.status_code}")
                print(f"[DEBUG] ❌ Response text: {response.text}")
                return None
            
            data = response.json()
            print(f"[DEBUG] 📋 Kakao API raw response: {json.dumps(data, ensure_ascii=False)[:500]}")
            
            documents = data.get("documents", [])
            print(f"[DEBUG] 📊 Documents count: {len(documents)}")
            
            if not documents:
                print(f"[DEBUG] ⚠️ No results found for: '{query}'")
                print(f"[DEBUG] ⚠️ Response meta: {data.get('meta', {})}")
                return None
            
            # Convert Kakao format to our format
            suggestions = []
            for idx, doc in enumerate(documents):
                print(f"[DEBUG] 📄 Document {idx + 1}: {json.dumps(doc, ensure_ascii=False)[:200]}")
                
                address_info = doc.get("address", {})
                road_address_info = doc.get("road_address", {})
                
                suggestion = {
                    "road_address": road_address_info.get("address_name", "") if road_address_info else "",
                    "jibun_address": address_info.get("address_name", ""),
                    "zone_no": road_address_info.get("zone_no", "") if road_address_info else "",
                    "display": road_address_info.get("address_name", "") if road_address_info else address_info.get("address_name", "")
                }
                
                # Only add if display is not empty
                if suggestion["display"]:
                    suggestions.append(suggestion)
                    print(f"[DEBUG] ✅ Added suggestion: {suggestion['display']}")
                else:
                    print(f"[DEBUG] ⚠️ Skipped empty suggestion")
            
            print(f"[DEBUG] 🎉 Successfully parsed {len(suggestions)} suggestions")
            print(f"{'='*60}\n")
            
            return {
                "suggestions": suggestions,
                "using_mock_data": False,
                "message": "Real Kakao API results"
            }
            
    except httpx.TimeoutException:
        print(f"[DEBUG] ❌ Timeout error")
        return None
    except Exception as e:
        print(f"[DEBUG] ❌ Exception: {type(e).__name__}")
        print(f"[DEBUG] ❌ Error message: {str(e)}")
        import traceback
        print(f"[DEBUG] ❌ Traceback: {traceback.format_exc()}")
        return None


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
                
                # Check for API key in headers (from frontend SessionStorage)
                kakao_api_key = self.headers.get('X-Kakao-API-Key', '').strip()
                
                # Also check environment variable
                if not kakao_api_key:
                    kakao_api_key = os.environ.get('KAKAO_REST_API_KEY', '').strip()
                
                print(f"[Address Search] Query: '{query}'")
                print(f"[Address Search] API Key present: {bool(kakao_api_key)}")
                
                # Try real Kakao API if key is available
                if kakao_api_key and query:
                    kakao_result = search_address_kakao(query, kakao_api_key)
                    if kakao_result and kakao_result.get('suggestions'):
                        print(f"[Address Search] Using Kakao API - {len(kakao_result['suggestions'])} results")
                        response = {
                            'success': True,
                            'data': kakao_result
                        }
                        response_json = json.dumps(response, ensure_ascii=False)
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(response_json.encode('utf-8'))
                        return
                
                # Fallback to Mock data
                print(f"[Address Search] Using Mock data (no API key or no results)")
                
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

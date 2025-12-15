"""
Kakao Maps Static Map Generator
Generate static map images for PDF reports
"""

import requests
from typing import Optional, List, Tuple
from io import BytesIO
import base64
from app.config_v30 import config_v30


class KakaoMapGenerator:
    """Generate static maps using Kakao Maps API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config_v30.KAKAO_REST_API_KEY
        self.static_map_url = "https://dapi.kakao.com/v2/maps/staticmap"
    
    def generate_static_map(
        self,
        lat: float,
        lng: float,
        width: int = 600,
        height: int = 400,
        level: int = 3,
        markers: Optional[List[Tuple[float, float, str]]] = None
    ) -> Optional[bytes]:
        """
        Generate a static map image
        
        Args:
            lat: Latitude of center point
            lng: Longitude of center point
            width: Map width in pixels (max 2048)
            height: Map height in pixels (max 2048)
            level: Zoom level (1-14, smaller = more zoomed in)
            markers: List of (lat, lng, label) tuples for markers
        
        Returns:
            bytes: PNG image data, or None if failed
        """
        
        # Build marker string
        marker_str = ""
        if markers:
            for idx, (m_lat, m_lng, label) in enumerate(markers):
                # Red marker for target property, blue for others
                color = "red" if idx == 0 else "blue"
                marker_str += f"marker{idx}:{m_lng},{m_lat},label:{label},color:{color}|"
            marker_str = marker_str.rstrip('|')
        else:
            # Single red marker for center
            marker_str = f"marker0:{lng},{lat},label:대상지,color:red"
        
        # API request
        url = self.static_map_url
        
        params = {
            "center": f"{lng},{lat}",
            "level": level,
            "w": width,
            "h": height,
            "marker": marker_str
        }
        
        headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ Kakao Static Map API error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return None
        
        except Exception as e:
            print(f"❌ Kakao Static Map API exception: {e}")
            return None
    
    def generate_poi_map(
        self,
        lat: float,
        lng: float,
        pois: List[dict],
        width: int = 600,
        height: int = 400
    ) -> Optional[bytes]:
        """
        Generate a map with POI markers
        
        Args:
            lat: Target property latitude
            lng: Target property longitude
            pois: List of POI dicts with 'lat', 'lng', 'name' keys
            width: Map width
            height: Map height
        
        Returns:
            bytes: PNG image data
        """
        
        # Build markers list
        markers = [(lat, lng, "대상지")]  # Target property (red)
        
        # Add POI markers (blue, max 10)
        for poi in pois[:10]:
            poi_name = poi.get('name', 'POI')[:5]  # Truncate to 5 chars
            markers.append((poi['lat'], poi['lng'], poi_name))
        
        return self.generate_static_map(
            lat, lng, width, height, level=4, markers=markers
        )
    
    def get_base64_image(
        self,
        lat: float,
        lng: float,
        width: int = 600,
        height: int = 400
    ) -> Optional[str]:
        """
        Get map as base64-encoded string (for HTML embedding)
        
        Returns:
            str: Base64-encoded PNG image data URI
        """
        
        image_bytes = self.generate_static_map(lat, lng, width, height)
        
        if image_bytes:
            base64_str = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:image/png;base64,{base64_str}"
        
        return None


def generate_placeholder_map(
    width: int = 600,
    height: int = 400,
    text: str = "지도 이미지"
) -> bytes:
    """
    Generate a placeholder map image when API fails
    
    This uses PIL to create a simple placeholder image
    """
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image
        img = Image.new('RGB', (width, height), color='#E8EAF6')
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([0, 0, width-1, height-1], outline='#1A237E', width=3)
        
        # Draw text
        text_bbox = draw.textbbox((0, 0), text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        draw.text((text_x, text_y), text, fill='#1A237E')
        
        # Draw map icon (simple marker)
        marker_x = width // 2
        marker_y = height // 2 - 50
        
        # Marker pin (triangle + circle)
        draw.ellipse([marker_x-15, marker_y-15, marker_x+15, marker_y+15], fill='#F44336')
        draw.polygon([marker_x, marker_y+15, marker_x-10, marker_y+30, marker_x+10, marker_y+30], fill='#F44336')
        
        # Save to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    except ImportError:
        # If PIL not available, return empty bytes
        print("⚠️ PIL not available, returning empty placeholder")
        return b''


# Example usage
if __name__ == "__main__":
    generator = KakaoMapGenerator()
    
    # Test coordinates (서울특별시 강남구 역삼동)
    lat, lng = 37.497942, 127.027619
    
    print(f"\n{'='*60}")
    print(f"Kakao Static Map API Test")
    print(f"{'='*60}")
    print(f"Coordinates: {lat}, {lng}")
    print(f"API Key: {generator.api_key[:20]}...")
    
    # Generate map
    map_bytes = generator.generate_static_map(lat, lng)
    
    if map_bytes:
        print(f"✅ SUCCESS: Generated map ({len(map_bytes):,} bytes)")
        
        # Save to file
        with open('/tmp/kakao_map_test.png', 'wb') as f:
            f.write(map_bytes)
        print(f"✅ Saved to: /tmp/kakao_map_test.png")
    else:
        print(f"❌ FAILED: Could not generate map")
        
        # Try placeholder
        placeholder = generate_placeholder_map()
        if placeholder:
            with open('/tmp/placeholder_map.png', 'wb') as f:
                f.write(placeholder)
            print(f"✅ Generated placeholder: /tmp/placeholder_map.png ({len(placeholder):,} bytes)")
    
    print(f"{'='*60}\n")

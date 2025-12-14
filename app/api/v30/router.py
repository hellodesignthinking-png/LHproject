"""
ZeroSite v30.0 - Complete API Router
Real National API Integration + 20-Page PDF
Single Address Input → Complete Appraisal
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import io

# Import all v30 engines
from app.engines.v30.geocoding_engine import GeocodingEngineV30
from app.engines.v30.zoning_engine import ZoningEngineV30
from app.engines.v30.landprice_engine import LandPriceEngineV30
from app.engines.v30.transaction_engine import TransactionEngineV30
from app.engines.v30.premium_engine import PremiumEngineV30
from app.engines.v30.appraisal_engine import AppraisalEngineV30

router_v30 = APIRouter(prefix="/api/v30", tags=["v30"])


# Request models
class AppraisalRequestV30(BaseModel):
    address: str
    land_area_sqm: Optional[float] = 400  # Default 400 sqm


# Initialize engines
geocoding_engine = GeocodingEngineV30()
zoning_engine = ZoningEngineV30()
landprice_engine = LandPriceEngineV30()
transaction_engine = TransactionEngineV30()
premium_engine = PremiumEngineV30()
appraisal_engine = AppraisalEngineV30()


@router_v30.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "30.0",
        "name": "ZeroSite v30.0 - Real National API + Full PDF Engine"
    }


@router_v30.post("/appraisal")
async def run_appraisal(request: AppraisalRequestV30):
    """
    Complete appraisal with single address input
    
    Steps:
    1. Geocoding (address → lat/lng)
    2. Zoning (lat/lng → zone_type)
    3. Land Price (lat/lng → official_price)
    4. Transactions (address → comparable sales)
    5. Premium Analysis
    6. Appraisal (3 approaches)
    
    Returns: Complete appraisal result with all data
    """
    try:
        address = request.address
        land_area = request.land_area_sqm
        
        # Step 1: Geocoding
        geo_result = geocoding_engine.geocode_address(address)
        if not geo_result['success']:
            raise HTTPException(status_code=400, detail="주소를 찾을 수 없습니다.")
        
        lat = geo_result['lat']
        lng = geo_result['lng']
        si = geo_result['si']
        gu = geo_result['gu']
        dong = geo_result['dong']
        jibun = geo_result['jibun']
        
        # Step 2: Zoning
        zone_result = zoning_engine.get_zone_type(lat, lng, si, gu, dong, jibun)
        zone_type = zone_result['zone_type']
        
        # Step 3: Land Price
        price_result = landprice_engine.get_land_price(lat, lng, '', si, gu, dong, jibun)
        official_price = price_result['official_price']
        price_year = price_result['year']
        
        # Step 4: Transactions
        transactions = transaction_engine.get_transactions(
            si, gu, dong, lat, lng, land_area, zone_type
        )
        
        # Step 5: Premium Analysis
        premium_result = premium_engine.analyze_premium(si, gu, dong, zone_type, lat, lng)
        
        # Step 6: Complete Appraisal
        land_info = {
            'address': address,
            'land_area': land_area,
            'official_price': official_price,
            'zone_type': zone_type,
            'lat': lat,
            'lng': lng
        }
        
        appraisal_result = appraisal_engine.run_appraisal(land_info, transactions, premium_result)
        
        # Construct response
        response = {
            'status': 'success',
            'version': 'v30.0 ULTIMATE - Real National API',
            'timestamp': import_time(),
            'land_info': {
                'address': address,
                'parsed_address': {
                    'si': si,
                    'gu': gu,
                    'dong': dong,
                    'jibun': jibun
                },
                'coordinates': {
                    'lat': lat,
                    'lng': lng
                },
                'land_area_sqm': land_area,
                'zone_type': zone_type,
                'official_land_price_per_sqm': int(official_price),
                'official_price_year': price_year,
                'geocoding_method': geo_result['method'],
                'zoning_method': zone_result['method'],
                'price_method': price_result['method']
            },
            'appraisal': {
                'final_value': appraisal_result['final_value'],
                'value_per_sqm': appraisal_result['value_per_sqm'],
                'confidence_level': appraisal_result['confidence_level'],
                'approaches': appraisal_result['approaches'],
                'weights': appraisal_result['weights'],
                'premium': appraisal_result['premium']
            },
            'comparable_sales': {
                'total_count': len(transactions),
                'transactions': transactions[:10]  # Top 10
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"평가 중 오류 발생: {str(e)}")


@router_v30.post("/appraisal/pdf")
async def generate_pdf(request: AppraisalRequestV30):
    """Generate 20-page PDF report"""
    try:
        # Get appraisal data
        appraisal_data = await run_appraisal(request)
        
        # Generate PDF (simplified for now - full implementation below)
        from app.services.v30.pdf_generator import PDFGeneratorV30
        pdf_generator = PDFGeneratorV30()
        pdf_bytes = pdf_generator.generate(appraisal_data)
        
        # Return PDF
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=appraisal_report_{import_time()}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 생성 오류: {str(e)}")


@router_v30.post("/appraisal/html")
async def generate_html(request: AppraisalRequestV30):
    """Generate HTML preview"""
    try:
        # Get appraisal data
        appraisal_data = await run_appraisal(request)
        
        # Generate HTML
        from app.services.v30.html_generator import HTMLGeneratorV30
        html_generator = HTMLGeneratorV30()
        html_content = html_generator.generate(appraisal_data)
        
        return {"html": html_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML 생성 오류: {str(e)}")


def import_time():
    """Get current timestamp"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

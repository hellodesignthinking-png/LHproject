"""
ZeroSite v30.0 - PDF Generator
Generate 20-page professional PDF report
"""
from typing import Dict
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io


class PDFGeneratorV30:
    """Generate 20-page professional PDF"""
    
    def generate(self, appraisal_data: Dict) -> bytes:
        """
        Generate PDF report
        
        Note: This is a simplified version.
        Full 20-page report would include:
        - Cover page
        - Executive summary
        - Land information (3 pages)
        - Zoning analysis (2 pages)
        - Land price analysis (2 pages)
        - Transaction comparison (3 pages)
        - Adjustments table (2 pages)
        - Cost approach (2 pages)
        - Sales comparison approach (2 pages)
        - Income approach (2 pages)
        - Premium analysis (1 page)
        - Final conclusion (1 page)
        """
        
        # Create PDF in memory
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Page 1: Cover
        self._draw_cover_page(pdf, width, height, appraisal_data)
        pdf.showPage()
        
        # Page 2: Executive Summary
        self._draw_summary_page(pdf, width, height, appraisal_data)
        pdf.showPage()
        
        # Page 3: Land Information
        self._draw_land_info_page(pdf, width, height, appraisal_data)
        pdf.showPage()
        
        # Page 4: Appraisal Results
        self._draw_appraisal_results(pdf, width, height, appraisal_data)
        pdf.showPage()
        
        # Page 5: Transactions
        self._draw_transactions_page(pdf, width, height, appraisal_data)
        pdf.showPage()
        
        # Additional pages would go here...
        # For v30.0, we'll provide 5 pages with key information
        
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _draw_cover_page(self, pdf: canvas.Canvas, width: float, height: float, data: Dict):
        """Draw cover page"""
        # Header
        pdf.setFillColorRGB(0.0, 0.36, 0.67)  # #005BAC
        pdf.rect(0, height - 150*mm, width, 150*mm, fill=True, stroke=False)
        
        # Title
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica-Bold", 32)
        pdf.drawCentredString(width/2, height - 80*mm, "Land Appraisal Report")
        
        pdf.setFont("Helvetica", 16)
        pdf.drawCentredString(width/2, height - 100*mm, data['version'])
        
        # Address
        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(width/2, height - 180*mm, data['land_info']['address'])
        
        # Date
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(width/2, 50*mm, f"Report Date: {data['timestamp']}")
    
    def _draw_summary_page(self, pdf: canvas.Canvas, width: float, height: float, data: Dict):
        """Draw executive summary"""
        y = height - 40*mm
        
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(30*mm, y, "Executive Summary")
        y -= 15*mm
        
        # Final value
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(30*mm, y, "Final Appraised Value:")
        y -= 8*mm
        
        pdf.setFont("Helvetica-Bold", 24)
        pdf.setFillColorRGB(0.0, 0.36, 0.67)
        final_value = data['appraisal']['final_value']
        pdf.drawString(40*mm, y, f"KRW {final_value:,}")
        y -= 12*mm
        
        # Value per sqm
        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Helvetica", 12)
        value_per_sqm = data['appraisal']['value_per_sqm']
        pdf.drawString(40*mm, y, f"(KRW {value_per_sqm:,} per sqm)")
        y -= 15*mm
        
        # Confidence
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30*mm, y, f"Confidence Level: {data['appraisal']['confidence_level']}")
    
    def _draw_land_info_page(self, pdf: canvas.Canvas, width: float, height: float, data: Dict):
        """Draw land information"""
        y = height - 40*mm
        
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(30*mm, y, "Land Information")
        y -= 15*mm
        
        land = data['land_info']
        
        info_items = [
            ("Address:", land['address']),
            ("Land Area:", f"{land['land_area_sqm']:,.1f} sqm"),
            ("Zone Type:", land['zone_type']),
            ("Official Land Price:", f"KRW {land['official_land_price_per_sqm']:,}/sqm ({land['official_price_year']})"),
            ("Coordinates:", f"Lat {land['coordinates']['lat']:.4f}, Lng {land['coordinates']['lng']:.4f}")
        ]
        
        pdf.setFont("Helvetica-Bold", 12)
        for label, value in info_items:
            pdf.drawString(30*mm, y, label)
            pdf.setFont("Helvetica", 12)
            pdf.drawString(70*mm, y, value)
            pdf.setFont("Helvetica-Bold", 12)
            y -= 8*mm
    
    def _draw_appraisal_results(self, pdf: canvas.Canvas, width: float, height: float, data: Dict):
        """Draw appraisal results"""
        y = height - 40*mm
        
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(30*mm, y, "Appraisal Approaches")
        y -= 15*mm
        
        approaches = data['appraisal']['approaches']
        weights = data['appraisal']['weights']
        
        # Cost Approach
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30*mm, y, "1. Cost Approach")
        y -= 8*mm
        pdf.setFont("Helvetica", 12)
        pdf.drawString(40*mm, y, f"Value: KRW {approaches['cost']['value']:,}")
        y -= 6*mm
        pdf.drawString(40*mm, y, f"Weight: {weights['cost']*100:.0f}%")
        y -= 12*mm
        
        # Sales Comparison
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30*mm, y, "2. Sales Comparison Approach")
        y -= 8*mm
        pdf.setFont("Helvetica", 12)
        pdf.drawString(40*mm, y, f"Value: KRW {approaches['sales_comparison']['value']:,}")
        y -= 6*mm
        pdf.drawString(40*mm, y, f"Weight: {weights['sales']*100:.0f}%")
        y -= 12*mm
        
        # Income Approach
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30*mm, y, "3. Income Approach")
        y -= 8*mm
        pdf.setFont("Helvetica", 12)
        pdf.drawString(40*mm, y, f"Value: KRW {approaches['income']['value']:,}")
        y -= 6*mm
        pdf.drawString(40*mm, y, f"Weight: {weights['income']*100:.0f}%")
        y -= 12*mm
        
        # Premium
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30*mm, y, "Location Premium")
        y -= 8*mm
        pdf.setFont("Helvetica", 12)
        premium = data['appraisal']['premium']['percentage']
        pdf.drawString(40*mm, y, f"+{premium}%")
    
    def _draw_transactions_page(self, pdf: canvas.Canvas, width: float, height: float, data: Dict):
        """Draw comparable transactions"""
        y = height - 40*mm
        
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(30*mm, y, "Comparable Sales")
        y -= 15*mm
        
        transactions = data['comparable_sales']['transactions'][:10]
        
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(30*mm, y, "Address")
        pdf.drawString(110*mm, y, "Size (sqm)")
        pdf.drawString(140*mm, y, "Price/sqm")
        y -= 6*mm
        
        pdf.setFont("Helvetica", 9)
        for trans in transactions:
            if y < 30*mm:
                break
            
            # Truncate long addresses
            addr = trans['address']
            if len(addr) > 40:
                addr = addr[:37] + "..."
            
            pdf.drawString(30*mm, y, addr)
            pdf.drawString(110*mm, y, f"{trans['size_sqm']:,.0f}")
            pdf.drawString(140*mm, y, f"₩{trans['price_per_sqm']:,.0f}")
            y -= 6*mm

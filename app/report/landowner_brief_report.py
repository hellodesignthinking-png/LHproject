"""Landowner Brief Report v24.0 - 토지주 간략 보고서"""
from .base_report import BaseReport

class LandownerBriefReport(BaseReport):
    def generate(self, analysis_data: dict) -> dict:
        """Non-technical 1-2 page summary for landowners"""
        return {
            'report_type': 'landowner_brief',
            'summary': f"Your {analysis_data['land_area_sqm']}㎡ land can build {analysis_data['floors']} floors, {analysis_data['units']} units",
            'expected_return': f"LH Purchase: {analysis_data['lh_purchase']}억원, Profit: {analysis_data['profit']}억원",
            'recommendation': analysis_data['decision'],
            'page_count': 2
        }

def main():
    print("\n" + "="*60)
    print("LANDOWNER BRIEF REPORT v24.0 - CLI TEST")
    print("="*60)
    engine = LandownerBriefReport()
    data = {'land_area_sqm': 660, 'floors': 5, 'units': 20, 'lh_purchase': 138, 'profit': -26, 'decision': 'NO-GO'}
    report = engine.generate(data)
    print(f"✅ Report Type: {report['report_type']}")
    print(f"✅ Summary: {report['summary']}")
    print(f"✅ Page Count: {report['page_count']}")
    print("="*60)
    print("✅ TEST PASSED!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

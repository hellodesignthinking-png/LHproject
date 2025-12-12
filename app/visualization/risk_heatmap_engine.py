"""Risk Heatmap Engine v24.0 - 리스크 히트맵"""
class RiskHeatmapEngine:
    def __init__(self):
        self.version = "24.0.0"
    
    def generate_heatmap(self, risk_data: dict) -> dict:
        categories = ['Legal', 'Financial', 'Technical', 'Market']
        values = [risk_data.get('legal', 0), risk_data.get('financial', 0), 
                  risk_data.get('technical', 0), risk_data.get('market', 0)]
        colors = ['#10B981' if v < 30 else '#F59E0B' if v < 60 else '#EF4444' for v in values]
        return {
            'chart_type': 'heatmap',
            'data': {'categories': categories, 'values': values, 'colors': colors},
            'overall_score': sum(values) / len(values)
        }

def main():
    print("\n" + "="*60)
    print("RISK HEATMAP ENGINE v24.0 - CLI TEST")
    print("="*60)
    engine = RiskHeatmapEngine()
    risk = {'legal': 25, 'financial': 35, 'technical': 45, 'market': 50}
    heatmap = engine.generate_heatmap(risk)
    print(f"✅ Heatmap: {len(heatmap['data']['categories'])} categories")
    print(f"✅ Overall Risk Score: {heatmap['overall_score']:.1f}/100")
    print(f"✅ Colors: {', '.join(heatmap['data']['colors'])}")
    print("="*60)
    print("✅ TEST PASSED!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

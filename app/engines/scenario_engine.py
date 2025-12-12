"""
Scenario Engine v24.0
시나리오 비교 엔진 for ZeroSite v24
"""
from typing import Dict, List
import logging
from .base_engine import BaseEngine

class ScenarioEngine(BaseEngine):
    def __init__(self):
        super().__init__(engine_name="ScenarioEngine", version="24.0")
    
    @property
    def timestamp(self):
        return self.created_at.isoformat()
    
    def process(self, input_data: Dict) -> Dict:
        self.validate_input(input_data, ['scenarios'])
        scenarios = input_data['scenarios']
        
        # Compare scenarios
        comparison = self._compare_scenarios(scenarios)
        best = self._find_best_scenario(comparison)
        
        result = {
            'success': True,
            'scenario_count': len(scenarios),
            'comparison': comparison,
            'best_scenario': best,
            'recommendation': f"✅ 권장안: {best['name']} (점수: {best['score']}/100)"
        }
        
        self.logger.info(f"Scenario analysis: {len(scenarios)} scenarios, best: {best['name']}")
        return result
    
    def _compare_scenarios(self, scenarios: List[Dict]) -> List[Dict]:
        results = []
        for i, s in enumerate(scenarios):
            score = (
                s.get('far', 200) * 0.3 +
                s.get('roi', 10) * 5 +
                (100 - s.get('risk', 30))
            ) / 2
            results.append({
                'id': i+1,
                'name': s.get('name', f'Scenario {i+1}'),
                'far': s.get('far', 200),
                'roi': s.get('roi', 10),
                'risk': s.get('risk', 30),
                'score': round(score, 1)
            })
        return results
    
    def _find_best_scenario(self, comparison: List[Dict]) -> Dict:
        return max(comparison, key=lambda x: x['score'])

if __name__ == "__main__":
    engine = ScenarioEngine()
    test = {
        'scenarios': [
            {'name': 'A안', 'far': 200, 'roi': 15, 'risk': 25},
            {'name': 'B안', 'far': 250, 'roi': 12, 'risk': 35},
            {'name': 'C안', 'far': 220, 'roi': 18, 'risk': 20}
        ]
    }
    result = engine.process(test)
    print(f"✅ {engine.engine_name} v{engine.version}")
    print(f"Best: {result['best_scenario']['name']} (Score: {result['best_scenario']['score']}/100)")
    print(result['recommendation'])

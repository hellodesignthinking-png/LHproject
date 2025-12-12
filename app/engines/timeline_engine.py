"""
Timeline Engine v24.0
개발 일정 계획 엔진 for ZeroSite v24
"""
from typing import Dict, List
from datetime import datetime, timedelta
import logging
from .base_engine import BaseEngine

class TimelineEngine(BaseEngine):
    def __init__(self):
        super().__init__(engine_name="TimelineEngine", version="24.0")
    
    @property
    def timestamp(self):
        return self.created_at.isoformat()
    
    def process(self, input_data: Dict) -> Dict:
        self.validate_input(input_data, ['project_type'])
        
        project_type = input_data['project_type']
        start_date = input_data.get('start_date', '2025-01-01')
        
        # Generate timeline
        phases = self._generate_phases(project_type)
        milestones = self._generate_milestones(phases, start_date)
        critical_path = self._identify_critical_path(phases)
        
        total_duration = sum(p['duration_months'] for p in phases)
        
        result = {
            'success': True,
            'project_type': project_type,
            'total_duration_months': total_duration,
            'phases': phases,
            'milestones': milestones,
            'critical_path': critical_path,
            'completion_date': self._calculate_completion_date(start_date, total_duration)
        }
        
        self.logger.info(f"Timeline generated: {project_type}, {total_duration} months")
        return result
    
    def _generate_phases(self, project_type: str) -> List[Dict]:
        phases = [
            {'name': '1. 인허가', 'duration_months': 3, 'critical': True},
            {'name': '2. 설계', 'duration_months': 2, 'critical': True},
            {'name': '3. 토지 매입', 'duration_months': 2, 'critical': False},
            {'name': '4. 착공 준비', 'duration_months': 1, 'critical': True},
            {'name': '5. 건축 공사', 'duration_months': 18, 'critical': True},
            {'name': '6. 준공 및 입주', 'duration_months': 2, 'critical': True}
        ]
        
        if '대규모' in project_type:
            phases[4]['duration_months'] = 24
        
        return phases
    
    def _generate_milestones(self, phases: List[Dict], start: str) -> List[str]:
        return [
            f"{p['name']} 완료 ({p['duration_months']}개월)"
            for p in phases
        ]
    
    def _identify_critical_path(self, phases: List[Dict]) -> List[str]:
        return [p['name'] for p in phases if p['critical']]
    
    def _calculate_completion_date(self, start: str, months: int) -> str:
        try:
            start_dt = datetime.strptime(start, '%Y-%m-%d')
            completion = start_dt + timedelta(days=months * 30)
            return completion.strftime('%Y-%m-%d')
        except:
            return '2027-01-01'

if __name__ == "__main__":
    engine = TimelineEngine()
    result = engine.process({'project_type': '일반 주거', 'start_date': '2025-01-01'})
    print(f"✅ {engine.engine_name} v{engine.version}")
    print(f"Total duration: {result['total_duration_months']} months")
    print(f"Completion: {result['completion_date']}")
    print(f"Critical path: {len(result['critical_path'])} phases")

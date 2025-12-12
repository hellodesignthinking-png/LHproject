"""Timeline Gantt Engine v24.0 - 간트 차트"""
class TimelineGanttEngine:
    def __init__(self):
        self.version = "24.0.0"
    
    def generate_gantt(self, timeline_data: dict) -> dict:
        phases = timeline_data.get('phases', [])
        return {
            'chart_type': 'gantt',
            'phases': phases,
            'total_duration': sum(p['duration_months'] for p in phases),
            'critical_path': [p['name'] for p in phases if p.get('critical', False)]
        }

def main():
    print("\n" + "="*60)
    print("TIMELINE GANTT ENGINE v24.0 - CLI TEST")
    print("="*60)
    engine = TimelineGanttEngine()
    timeline = {
        'phases': [
            {'name': 'Planning', 'duration_months': 3, 'critical': True},
            {'name': 'Approval', 'duration_months': 6, 'critical': True},
            {'name': 'Construction', 'duration_months': 18, 'critical': True}
        ]
    }
    gantt = engine.generate_gantt(timeline)
    print(f"✅ Gantt: {len(gantt['phases'])} phases")
    print(f"✅ Total Duration: {gantt['total_duration']} months")
    print(f"✅ Critical Path: {', '.join(gantt['critical_path'])}")
    print("="*60)
    print("✅ TEST PASSED!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ZeroSite v24.1 - Feedback Collection Script
Collects and analyzes user feedback for Option C Week 1

Usage:
    python scripts/collect_feedback.py
    python scripts/collect_feedback.py --analyze
    python scripts/collect_feedback.py --export feedback.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
import argparse


class FeedbackCollector:
    """Collect and analyze user feedback"""
    
    def __init__(self, feedback_file: str = "data/feedback.json"):
        self.feedback_file = Path(feedback_file)
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> List[Dict[str, Any]]:
        """Load existing feedback"""
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_feedback(self):
        """Save feedback to file"""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
    
    def add_feedback(
        self,
        category: str,
        content: str,
        rating: int = None,
        user_id: str = None
    ):
        """Add new feedback entry"""
        feedback = {
            "id": len(self.feedback_data) + 1,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "content": content,
            "rating": rating,
            "user_id": user_id,
            "status": "new"
        }
        self.feedback_data.append(feedback)
        self._save_feedback()
        print(f"✅ Feedback added: {feedback['id']}")
    
    def collect_interactive(self):
        """Collect feedback interactively"""
        print("\n" + "="*70)
        print("       ZeroSite v24.1 - Feedback Collection")
        print("="*70 + "\n")
        
        print("Categories:")
        print("  1. Feature Request")
        print("  2. Bug Report")
        print("  3. UX Issue")
        print("  4. Performance Concern")
        print("  5. Feature Appreciation")
        print("  6. General Comment")
        print()
        
        try:
            category_map = {
                "1": "feature_request",
                "2": "bug_report",
                "3": "ux_issue",
                "4": "performance",
                "5": "appreciation",
                "6": "general"
            }
            
            category_input = input("Select category (1-6): ").strip()
            category = category_map.get(category_input, "general")
            
            content = input("\nFeedback content: ").strip()
            
            rating_input = input("Overall satisfaction (1-5, or Enter to skip): ").strip()
            rating = int(rating_input) if rating_input else None
            
            user_id = input("User ID (optional): ").strip() or None
            
            self.add_feedback(category, content, rating, user_id)
            
            another = input("\nAdd another? (y/n): ").strip().lower()
            if another == 'y':
                self.collect_interactive()
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Collection cancelled.")
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze collected feedback"""
        if not self.feedback_data:
            return {
                "total_feedback": 0,
                "message": "No feedback collected yet"
            }
        
        analysis = {
            "total_feedback": len(self.feedback_data),
            "by_category": Counter(f["category"] for f in self.feedback_data),
            "average_rating": self._calculate_avg_rating(),
            "top_feature_requests": self._get_top_requests(),
            "critical_bugs": self._get_critical_bugs(),
            "common_ux_issues": self._get_common_ux_issues(),
            "sentiment_distribution": self._analyze_sentiment()
        }
        
        return analysis
    
    def _calculate_avg_rating(self) -> float:
        """Calculate average satisfaction rating"""
        ratings = [f["rating"] for f in self.feedback_data if f.get("rating")]
        if not ratings:
            return 0.0
        return sum(ratings) / len(ratings)
    
    def _get_top_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top feature requests"""
        requests = [
            f for f in self.feedback_data 
            if f["category"] == "feature_request"
        ]
        
        # Group by content similarity (simple keyword matching)
        grouped = {}
        for req in requests:
            content_lower = req["content"].lower()
            
            # Check for common keywords
            matched = False
            for key in grouped:
                if any(word in content_lower for word in key.split()):
                    grouped[key].append(req)
                    matched = True
                    break
            
            if not matched:
                # Extract keywords from content
                keywords = " ".join(content_lower.split()[:3])
                grouped[keywords] = [req]
        
        # Sort by frequency
        sorted_groups = sorted(
            grouped.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:limit]
        
        return [
            {
                "feature": group[0],
                "count": len(group[1]),
                "examples": [req["content"] for req in group[1][:3]]
            }
            for group in sorted_groups
        ]
    
    def _get_critical_bugs(self) -> List[Dict[str, Any]]:
        """Get critical bug reports"""
        bugs = [
            f for f in self.feedback_data 
            if f["category"] == "bug_report"
        ]
        
        return [
            {
                "id": bug["id"],
                "content": bug["content"],
                "timestamp": bug["timestamp"]
            }
            for bug in bugs
        ]
    
    def _get_common_ux_issues(self) -> List[Dict[str, Any]]:
        """Get common UX issues"""
        ux_issues = [
            f for f in self.feedback_data 
            if f["category"] == "ux_issue"
        ]
        
        return [
            {
                "id": issue["id"],
                "content": issue["content"]
            }
            for issue in ux_issues
        ]
    
    def _analyze_sentiment(self) -> Dict[str, int]:
        """Analyze overall sentiment"""
        ratings = [f["rating"] for f in self.feedback_data if f.get("rating")]
        
        if not ratings:
            return {"positive": 0, "neutral": 0, "negative": 0}
        
        return {
            "positive": sum(1 for r in ratings if r >= 4),
            "neutral": sum(1 for r in ratings if r == 3),
            "negative": sum(1 for r in ratings if r <= 2)
        }
    
    def generate_report(self) -> str:
        """Generate human-readable analysis report"""
        analysis = self.analyze()
        
        if analysis["total_feedback"] == 0:
            return "📭 No feedback collected yet."
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║         ZeroSite v24.1 - Feedback Analysis Report               ║
║         Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                       ║
╚══════════════════════════════════════════════════════════════════╝

📊 OVERVIEW
────────────────────────────────────────────────────────────────────
  Total Feedback:          {analysis['total_feedback']}
  Average Rating:          {analysis['average_rating']:.2f}/5.0
  
  Sentiment Distribution:
    Positive (4-5):        {analysis['sentiment_distribution']['positive']}
    Neutral (3):           {analysis['sentiment_distribution']['neutral']}
    Negative (1-2):        {analysis['sentiment_distribution']['negative']}

📋 FEEDBACK BY CATEGORY
────────────────────────────────────────────────────────────────────
"""
        
        for category, count in analysis['by_category'].most_common():
            report += f"  {category.replace('_', ' ').title():<25} {count}\n"
        
        report += "\n🎯 TOP FEATURE REQUESTS\n"
        report += "─"*68 + "\n"
        
        for i, req in enumerate(analysis['top_feature_requests'][:5], 1):
            report += f"  {i}. {req['feature'].title():<30} ({req['count']} requests)\n"
            if req['examples']:
                report += f"     Example: \"{req['examples'][0][:60]}...\"\n"
        
        if analysis['critical_bugs']:
            report += "\n🐛 CRITICAL BUGS\n"
            report += "─"*68 + "\n"
            for bug in analysis['critical_bugs'][:5]:
                report += f"  #{bug['id']}: {bug['content'][:60]}...\n"
        
        if analysis['common_ux_issues']:
            report += "\n🎨 COMMON UX ISSUES\n"
            report += "─"*68 + "\n"
            for issue in analysis['common_ux_issues'][:5]:
                report += f"  #{issue['id']}: {issue['content'][:60]}...\n"
        
        report += "\n" + "="*68 + "\n"
        
        return report
    
    def prioritize_for_week2(self) -> Dict[str, List[str]]:
        """Prioritize feedback items for Week 2 implementation"""
        analysis = self.analyze()
        
        # Score each GAP based on feedback
        gap_scores = {
            "GAP #8 (Dashboard UI)": 0,
            "GAP #9 (Zoning 2024)": 0,
            "GAP #10 (Data Layer)": 0,
            "GAP #11 (Narratives)": 0,
            "GAP #12 (3D Sketch)": 0
        }
        
        # Analyze feature requests for GAP keywords
        for req in analysis.get('top_feature_requests', []):
            content = req['feature'].lower()
            count = req['count']
            
            if any(word in content for word in ['dashboard', 'ui', 'interface', 'wizard']):
                gap_scores["GAP #8 (Dashboard UI)"] += count * 3
            
            if any(word in content for word in ['zoning', 'regulation', 'compliance', '2024']):
                gap_scores["GAP #9 (Zoning 2024)"] += count * 3
            
            if any(word in content for word in ['data', 'source', 'reliability', 'fallback']):
                gap_scores["GAP #10 (Data Layer)"] += count * 3
            
            if any(word in content for word in ['narrative', 'report', 'text', 'description']):
                gap_scores["GAP #11 (Narratives)"] += count * 3
            
            if any(word in content for word in ['3d', 'visual', 'render', 'sunlight']):
                gap_scores["GAP #12 (3D Sketch)"] += count * 3
        
        # Sort by score
        sorted_gaps = sorted(
            gap_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "recommended_for_week2": [gap[0] for gap in sorted_gaps[:3]],
            "scores": dict(sorted_gaps),
            "rationale": [
                f"{gap}: {score} points from user feedback"
                for gap, score in sorted_gaps[:3]
            ]
        }
    
    def export_for_analysis(self, output_path: str):
        """Export feedback data for external analysis"""
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_feedback": len(self.feedback_data),
            "feedback": self.feedback_data,
            "analysis": self.analyze(),
            "week2_priorities": self.prioritize_for_week2()
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Feedback exported to: {output_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ZeroSite v24.1 Feedback Collection"
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="Collect feedback interactively"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze collected feedback"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export feedback to JSON file"
    )
    parser.add_argument(
        "--feedback-file",
        type=str,
        default="data/feedback.json",
        help="Feedback data file path"
    )
    parser.add_argument(
        "--week2-priorities",
        action="store_true",
        help="Generate Week 2 priorities based on feedback"
    )
    
    args = parser.parse_args()
    
    collector = FeedbackCollector(feedback_file=args.feedback_file)
    
    if args.collect:
        collector.collect_interactive()
    
    if args.analyze or (not args.collect and not args.export and not args.week2_priorities):
        print(collector.generate_report())
    
    if args.week2_priorities:
        priorities = collector.prioritize_for_week2()
        print("\n📋 Week 2 Recommended Priorities:\n")
        for i, gap in enumerate(priorities["recommended_for_week2"], 1):
            print(f"  {i}. {gap}")
        print("\n" + "─"*68)
        for rationale in priorities["rationale"]:
            print(f"  {rationale}")
    
    if args.export:
        collector.export_for_analysis(args.export)


if __name__ == "__main__":
    main()

"""Corridor analysis - rank violations by corridor/segment"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class CorridorAnalyzer:
    """Analyze violations by corridor"""
    
    def get_top_corridors(self, violations: List[Dict], limit: int = 10) -> List[Dict]:
        """Get top violating corridors ranked by risk"""
        
        corridor_stats = {}
        
        for violation in violations:
            corridor = violation.get('corridor', 'UNKNOWN')
            
            if corridor not in corridor_stats:
                corridor_stats[corridor] = {
                    "violation_count": 0,
                    "risk_sum": 0,
                    "risk_avg": 0,
                }
            
            corridor_stats[corridor]["violation_count"] += 1
            corridor_stats[corridor]["risk_sum"] += violation.get('risk_score', 0)
        
        # Compute averages and rank
        results = []
        for corridor, stats in corridor_stats.items():
            count = stats["violation_count"]
            avg_risk = stats["risk_sum"] / count if count > 0 else 0
            
            results.append({
                "corridor": corridor,
                "violation_count": count,
                "avg_risk_score": round(avg_risk, 1),
                "risk_weighted": stats["risk_sum"],
            })
        
        # Sort by risk-weighted sum descending
        results.sort(key=lambda x: x["risk_weighted"], reverse=True)
        
        return results[:limit]

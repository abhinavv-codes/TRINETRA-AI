"""Trend analysis - time-series aggregation"""

import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyze violation trends over time"""
    
    def get_hourly_trends(self, violations: List[Dict]) -> List[Dict]:
        """Get hourly violation trends"""
        
        hourly_stats = {}
        
        for violation in violations:
            timestamp = violation.get('detected_at')
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp)
            else:
                dt = timestamp
            
            hour_key = dt.strftime("%Y-%m-%d %H:00")
            
            if hour_key not in hourly_stats:
                hourly_stats[hour_key] = {
                    "count": 0,
                    "risk_sum": 0,
                    "risk_avg": 0,
                }
            
            hourly_stats[hour_key]["count"] += 1
            hourly_stats[hour_key]["risk_sum"] += violation.get('risk_score', 0)
        
        # Compute averages
        for key in hourly_stats:
            count = hourly_stats[key]["count"]
            hourly_stats[key]["risk_avg"] = hourly_stats[key]["risk_sum"] / count if count > 0 else 0
        
        return [
            {
                "timestamp": k,
                "count": v["count"],
                "risk_avg": round(v["risk_avg"], 1),
            }
            for k, v in sorted(hourly_stats.items())
        ]

"""Report generation - NL reports and evidence annotation"""

import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate natural language enforcement reports"""
    
    # Report templates
    TEMPLATES = {
        "NO_HELMET": "{vehicle_type} ({plate}) detected without helmet at {time}",
        "TRIPLE_RIDING": "{vehicle_type} ({plate}) carrying {count} riders at {time}",
        "RED_LIGHT": "{vehicle_type} ({plate}) jumped red light at {time}",
        "WRONG_SIDE": "{vehicle_type} ({plate}) driving wrong-side at {time}",
        "ILLEGAL_PARKING": "Vehicle ({plate}) parked illegally at {time}",
    }
    
    def generate_report(self, event: Dict) -> str:
        """
        Generate natural language report for violation
        
        Args:
            event: Violation event dictionary
        
        Returns:
            Natural language report string
        """
        
        violations = event.get('violations', [])
        if not violations:
            return ""
        
        primary_violation = violations[0]
        template = self.TEMPLATES.get(primary_violation, "Violation detected")
        
        report = f"{template}\n"
        report += f"Risk Score: {event.get('risk_score', 0)}/100 ({event.get('risk_band', 'UNKNOWN')})\n"
        report += f"Camera: {event.get('camera_id', 'UNKNOWN')}\n"
        
        if event.get('ped_count', 0) > 0:
            report += f"Pedestrians nearby: {event['ped_count']}\n"
        
        if 'SCHOOL_ZONE' in event.get('zones', []):
            report += "Location: SCHOOL ZONE (high priority)\n"
        
        report += f"Evidence: {event.get('evidence_uri', 'N/A')}\n"
        report += f"Status: {event.get('status', 'PENDING')}\n"
        
        return report
    
    def generate_summary(self, violations_list: list) -> Dict:
        """Generate daily summary report"""
        
        total = len(violations_list)
        high_risk = len([v for v in violations_list if v.get('risk_score', 0) >= 60])
        critical = len([v for v in violations_list if v.get('risk_score', 0) >= 80])
        
        avg_risk = sum([v.get('risk_score', 0) for v in violations_list]) / total if total > 0 else 0
        
        return {
            "date": datetime.utcnow().date().isoformat(),
            "total_violations": total,
            "high_risk": high_risk,
            "critical": critical,
            "average_risk_score": round(avg_risk, 1),
            "timestamp": datetime.utcnow().isoformat(),
        }

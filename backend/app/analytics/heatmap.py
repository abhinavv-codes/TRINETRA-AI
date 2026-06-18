"""Heatmap generator - KDE for violation hotspots"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class HeatmapGenerator:
    """Generate KDE hotspot heatmaps"""
    
    def generate_geojson(self, violations: List[Dict]) -> Dict:
        """
        Generate GeoJSON heatmap from violations
        
        Args:
            violations: List of violation events with location
        
        Returns:
            GeoJSON FeatureCollection
        """
        
        features = []
        
        for violation in violations:
            location = violation.get('location')
            if not location:
                continue
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [location['lon'], location['lat']]
                },
                "properties": {
                    "violation_id": violation['violation_id'],
                    "risk_score": violation['risk_score'],
                    "violation_type": violation['violations'][0] if violation['violations'] else 'UNKNOWN',
                }
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }

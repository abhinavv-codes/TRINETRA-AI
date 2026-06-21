import sys
import os
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.engine.violations import ViolationEngine
from app.core.constants import ViolationType

def test_triple_riding_detection():
    print("--- Running Test for Triple Riding Detection Logic ---")
    engine = ViolationEngine()
    
    # 1. Setup mock detections containing 1 motorcycle and 3 overlapping persons
    # Bounding boxes format: [x1, y1, x2, y2]
    motorcycle_box = [100.0, 200.0, 300.0, 400.0]
    person1_box = [110.0, 210.0, 180.0, 380.0] # Overlaps
    person2_box = [190.0, 210.0, 260.0, 380.0] # Overlaps
    person3_box = [240.0, 210.0, 290.0, 380.0] # Overlaps
    
    # Detections structure
    detections = {
        "boxes": np.array([
            motorcycle_box,
            person1_box,
            person2_box,
            person3_box
        ]),
        "classes": np.array([3, 0, 0, 0]), # 3 = motorcycle, 0 = person
        "confidences": np.array([0.9, 0.85, 0.88, 0.92]),
        "class_names": {3: "motorcycle", 0: "person"}
    }
    
    # Run the engine
    vehicles = engine.detect_violations(detections)
    
    print(f"Detected vehicles with violations:")
    for v in vehicles:
        print(f"Vehicle type: {v['class_name']}")
        print(f"Violations: {v['violations']}")
        print(f"Violation Details: {v['violation_details']}")
        
    # Assertions
    assert len(vehicles) == 1, "Should detect 1 vehicle"
    assert ViolationType.TRIPLE_RIDING.value in vehicles[0]['violations'], "Triple riding violation should be detected!"
    print("[SUCCESS] Triple Riding Detection Test Passed successfully!")

if __name__ == "__main__":
    test_triple_riding_detection()

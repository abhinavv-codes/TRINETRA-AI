import sys
import os
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.engine.violations import ViolationEngine, associate_plates_to_vehicles
from app.core.constants import ViolationType

def test_multi_vehicle_association_and_violations():
    print("--- Running Test for Multi-Vehicle Plate Association & Violations ---")
    engine = ViolationEngine()

    # 1. Coordinate Definitions:
    # Bike 1 (Center: 200, 200)
    bike1_box = [100.0, 100.0, 300.0, 300.0]
    # Bike 2 (Center: 700, 700)
    bike2_box = [600.0, 600.0, 800.0, 800.0]
    # Car 3 (Center: 1100, 200)
    car3_box = [1000.0, 100.0, 1200.0, 300.0]

    # Plate 1: nearest to Bike 1 (Center: 200, 295)
    plate1_box = [150.0, 280.0, 250.0, 310.0]
    # Plate 2: nearest to Bike 2 (Center: 700, 795)
    plate2_box = [650.0, 780.0, 750.0, 810.0]

    # Persons:
    # 3 persons associated with Bike 1 -> Should trigger TRIPLE_RIDING
    p1 = [110.0, 110.0, 150.0, 280.0]
    p2 = [160.0, 110.0, 200.0, 280.0]
    p3 = [210.0, 110.0, 250.0, 280.0]
    # 1 person associated with Bike 2
    p4 = [610.0, 610.0, 650.0, 780.0]

    # Custom no-helmet detection: overlaps with Bike 2 -> Should trigger NO_HELMET
    no_helmet_box = [620.0, 620.0, 640.0, 640.0]

    # Combined detections dict
    detections = {
        "boxes": np.array([
            bike1_box,
            bike2_box,
            car3_box,
            plate1_box,
            plate2_box,
            p1, p2, p3, p4,
            no_helmet_box
        ]),
        "classes": np.array([
            1000, 1000, 2, # 1000 = bike, 2 = car
            2000, 2000,     # 2000 = License_Plate
            0, 0, 0, 0,     # 0 = person
            1002            # 1002 = no-helmet
        ]),
        "confidences": np.array([
            0.95, 0.90, 0.88,
            0.92, 0.94,
            0.90, 0.89, 0.91, 0.85,
            0.87
        ]),
        "class_names": {
            0: "person",
            2: "car",
            1000: "bike",
            1002: "no-helmet",
            2000: "License_Plate"
        }
    }

    # Verify helper function directly first
    vehicle_boxes = [bike1_box, bike2_box, car3_box]
    plate_boxes = [plate1_box, plate2_box]
    v_to_plate = associate_plates_to_vehicles(vehicle_boxes, plate_boxes)

    assert v_to_plate[0] == plate1_box, "Plate 1 should be associated with Bike 1"
    assert v_to_plate[1] == plate2_box, "Plate 2 should be associated with Bike 2"
    assert 2 not in v_to_plate, "Car 3 should not have any associated plate"
    print("[SUCCESS] Direct associate_plates_to_vehicles test passed!")

    # Run the engine
    vehicles = engine.detect_violations(detections)

    assert len(vehicles) == 3, f"Should process all 3 vehicles, found {len(vehicles)}"

    # Sort vehicles by box x1 coordinate to check them deterministically
    vehicles.sort(key=lambda x: x['box'][0])
    v_bike1 = vehicles[0]
    v_bike2 = vehicles[1]
    v_car3 = vehicles[2]

    # Verify Bike 1: TRIPLE_RIDING
    print(f"\nVehicle 1 ({v_bike1['class_name']}):")
    print(f"  Violations: {v_bike1['violations']}")
    print(f"  Associated Plate Box: {v_bike1['associated_plate_box']}")
    assert ViolationType.TRIPLE_RIDING.value in v_bike1['violations'], "Bike 1 should have TRIPLE_RIDING"
    assert v_bike1['associated_plate_box'] == plate1_box, "Bike 1 should map to Plate 1"

    # Verify Bike 2: NO_HELMET
    print(f"\nVehicle 2 ({v_bike2['class_name']}):")
    print(f"  Violations: {v_bike2['violations']}")
    print(f"  Associated Plate Box: {v_bike2['associated_plate_box']}")
    assert ViolationType.NO_HELMET.value in v_bike2['violations'], "Bike 2 should have NO_HELMET"
    assert v_bike2['associated_plate_box'] == plate2_box, "Bike 2 should map to Plate 2"

    # Verify Car 3: Clean
    print(f"\nVehicle 3 ({v_car3['class_name']}):")
    print(f"  Violations: {v_car3['violations']}")
    print(f"  Associated Plate Box: {v_car3['associated_plate_box']}")
    assert len(v_car3['violations']) == 0, "Car 3 should be clean"
    assert v_car3['associated_plate_box'] is None, "Car 3 should have no plate"

    print("\n[SUCCESS] Multi-Vehicle Association & Violations Unit Test Passed successfully!")

if __name__ == "__main__":
    test_multi_vehicle_association_and_violations()

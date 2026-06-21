# TRINETRA AI Active Violation Matrix

This document outlines the code paths capable of generating or exposing unsupported violations (RED_LIGHT, ILLEGAL_PARKING, WRONG_SIDE, STOP_LINE, SEATBELT) and specifies our strategy to disable them.

---

## 1. Supported Traffic Violations (Flipkart GRID Target)

The system officially supports *only*:
1.  `NO_HELMET`
2.  `TRIPLE_RIDING`

License plate detection (`LICENSE_PLATE_OCR`) is supported as a system pipeline feature but is not a standalone traffic infraction type.

---

## 2. Violation Code Paths & Disabling Plan

### A. RED_LIGHT (Red Light Jump)
*   **Generation Code Path**: `detect_red_light_jump(self, vehicle, traffic_lights, image)` in [violations.py](file:///d:/GRIDLOCK/backend/app/engine/violations.py#L183).
*   **Invocation**: Called inside `detect_violations` at line 332.
*   **Disabling Action**: Update the method to immediately return `None`, bypassing color detection heuristics.

### B. ILLEGAL_PARKING (Illegal Parking)
*   **Generation Code Path**: `detect_illegal_parking(self, vehicle, detections)` in [violations.py](file:///d:/GRIDLOCK/backend/app/engine/violations.py#L200).
*   **Invocation**: Called inside `detect_violations` at line 338.
*   **Disabling Action**: Keep the method returning `None` to bypass heuristics.

### C. WRONG_SIDE (Wrong Side Driving)
*   **Generation Code Path**: `detect_wrong_side(self, vehicle)` in [violations.py](file:///d:/GRIDLOCK/backend/app/engine/violations.py#L175).
*   **Invocation**: Called inside `detect_violations` at line 320.
*   **Disabling Action**: Keep the method returning `None` to bypass heuristics.

### D. STOP_LINE (Stop Line Crossing)
*   **Generation Code Path**: `detect_stop_line(self, vehicle, detections)` in [violations.py](file:///d:/GRIDLOCK/backend/app/engine/violations.py#L179).
*   **Invocation**: Called inside `detect_violations` at line 326.
*   **Disabling Action**: Keep the method returning `None` to bypass line crossing math.

### E. SEATBELT / NO_SEATBELT (Seatbelt Detection)
*   **Generation Code Path**: `detect_no_seatbelt(self, vehicle, persons, detections)` in [violations.py](file:///d:/GRIDLOCK/backend/app/engine/violations.py#L171).
*   **Invocation**: Called inside `detect_violations` at line 313.
*   **Disabling Action**: Keep the method returning `None` (model getter is already stubbed).

---

## 3. Cleansing Historical Records (API Filtering)

Audit checks on the SQLite database (`trinetra.db`) reveal that existing seed and test entries contain historical `RED_LIGHT`, `WRONG_SIDE`, and `ILLEGAL_PARKING` classifications. To satisfy the requirement that *only supported violations appear in API responses*, we will implement active filters inside backend router logic:

### A. Telemetry Listings (`/api/v1/violations/list` & `/api/v1/violations/{violation_id}`)
*   **Target**: [violations.py](file:///d:/GRIDLOCK/backend/app/routers/violations.py)
*   **Filtering**: Filter the `violation_types` list so it contains only `NO_HELMET` and `TRIPLE_RIDING`. If a record contains *only* unsupported violations, it will be skipped from the `/list` response array. If requested directly via `/id`, we will return a `404 Not Found` (or raise HTTP Exception).

### B. Dashboard Statistics (`/api/v1/analytics/statistics`)
*   **Target**: [analytics.py](file:///d:/GRIDLOCK/backend/app/routers/analytics.py)
*   **Filtering**: Query records and perform a python filter step, keeping only violations with supported types. Recalculate totals, daily metrics, and averages using this filtered set. Cleanse the fallback metrics object to remove `RED_LIGHT` and `NO_SEATBELT` keys.

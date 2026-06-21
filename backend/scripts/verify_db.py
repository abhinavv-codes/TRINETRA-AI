import sqlite3
import json
import os

db_path = "trinetra.db"

def verify():
    print("--- Database Verification Script ---")
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query last 3 violations
    cursor.execute("""
        SELECT v.violation_id, v.violation_types, v.risk_score, v.risk_band, v.metadata_json, veh.plate_text, veh.vehicle_type
        FROM violations v
        LEFT JOIN vehicles veh ON v.vehicle_id = veh.vehicle_id
        ORDER BY v.detected_at DESC
        LIMIT 3
    """)
    
    rows = cursor.fetchall()
    print(f"\nLast {len(rows)} Violations Written to Database:")
    for row in rows:
        v_id, v_types, risk, band, meta, plate, v_type = row
        print(f"\nViolation ID: {v_id}")
        print(f"Vehicle: {v_type} (Plate: {plate})")
        print(f"Violation Types: {v_types}")
        print(f"Risk Band: {band} (Score: {risk})")
        print("Metadata JSON (factors):")
        try:
            meta_dict = json.loads(meta) if meta else {}
            print(json.dumps(meta_dict, indent=2))
        except Exception as e:
            print(f"  Error parsing metadata: {e}")
            print(f"  Raw: {meta}")

    # Query last 3 evidence files
    cursor.execute("""
        SELECT evidence_id, violation_id, image_uri, sha256, metadata_json
        FROM evidence
        ORDER BY created_at DESC
        LIMIT 3
    """)
    rows_ev = cursor.fetchall()
    print(f"\nLast {len(rows_ev)} Evidence Records:")
    for r in rows_ev:
        ev_id, viol_id, uri, sha, meta_ev = r
        print(f"Evidence ID: {ev_id} | Violation ID: {viol_id}")
        print(f"  Image URI: {uri}")
        print(f"  SHA-256 Hash: {sha}")
        print(f"  Evidence Metadata: {meta_ev}")

    conn.close()

if __name__ == "__main__":
    verify()

import sys
import os
import json
import cv2
import numpy as np
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

def create_mock_video(path):
    print(f"Creating mock video at {path}...")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, 10.0, (640, 480))
    for i in range(15):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, f"Frame {i}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        out.write(frame)
    out.release()
    print("Mock video created.")

def run_tests():
    client = TestClient(app)
    
    # 1. Test Image Detection
    image_path = r"C:\Users\acer\.gemini\antigravity-ide\brain\5136487d-2184-4108-835d-85d84a5d4499\traffic_motorcycle_1781883048249.png"
    print(f"\n--- TESTING /api/v1/violations/detect with image {image_path} ---")
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            file_bytes = f.read()
        response = client.post(
            "/api/v1/violations/detect",
            files={"file": ("traffic_motorcycle.png", file_bytes, "image/png")},
            data={"camera_id": "J17-N"}
        )
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Image {image_path} not found.")

    # 2. Test Video Detection
    video_path = "test_video.mp4"
    create_mock_video(video_path)
    print("\n--- TESTING /api/v1/violations/detect-video ---")
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    response = client.post(
        "/api/v1/violations/detect-video",
        files={"file": ("test_video.mp4", video_bytes, "video/mp4")},
        data={"camera_id": "J17-N"}
    )
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
    
    if os.path.exists(video_path):
        os.remove(video_path)

    # 3. Test Live Stream Support
    print("\n--- TESTING /api/v1/violations/live ---")
    response = client.post(
        "/api/v1/violations/live",
        json={"source": "0", "duration_seconds": 1}
    )
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))

    # 4. Test Analytics Statistics
    print("\n--- TESTING /api/v1/analytics/statistics ---")
    response = client.get("/api/v1/analytics/statistics")
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    run_tests()

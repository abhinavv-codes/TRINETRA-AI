from fastapi import FastAPI,UploadFile, File
import tempfile
import cv2
import base64

from app.inference.enhancement import process_video

app=FastAPI()

@app.post("/test-enhancement")
async def test_enhancement(
    video: UploadFile = File(...)
):
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    ) as temp:

        temp.write(
            await video.read()
        )

        video_path = temp.name

    frames = []

    for i, result in enumerate(
        process_video(video_path)
    ):

        enhanced_frame = result["frame"]

        _, buffer = cv2.imencode(
            ".jpg",
            enhanced_frame
        )

        frames.append(
            base64.b64encode(
                buffer
            ).decode("utf-8")
        )

        if i == 9:
            break

    return {
        "frames": frames
    }
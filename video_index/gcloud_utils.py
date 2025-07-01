# video_index/gcloud_utils.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from .get_frame import get_frame_from_urls

app = FastAPI()


@app.get("/frame")
async def serve_frame(
    video_url: str = Query(..., description="URL to the AV1 intra-only video file"),
    index_url: str = Query(..., description="URL to the binary frame index file"),
    frame: int = Query(..., ge=0, description="Frame number to retrieve"),
):
    """
    Serve a single raw AV1 frame from video_url at the given frame number,
    using the binary index file at index_url.
    """
    try:
        frame_bytes = get_frame_from_urls(video_url, index_url, frame)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return StreamingResponse(io.BytesIO(frame_bytes), media_type="video/AV1")


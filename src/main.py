import logging
from io import BytesIO
from uuid import UUID

import aiohttp
from pydantic import BaseModel
from asset_manager.storage import FileStorageEngine
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

logger = logging.getLogger("uvicorn")


app = FastAPI()
storage_engine = FileStorageEngine()


@app.get("/health")
async def health_check():
    return {"status": "UP"}


@app.post("/assets")
async def upload_image(file: UploadFile = File(...)):
    image_id = storage_engine.save_file(file.file)
    return {"id": image_id, "url": f"/assets/{image_id}"}


class UpsertImageRequest(BaseModel):
    id: str
    url: str


@app.post("/assets/upsert")
async def upsert_image(request: UpsertImageRequest):
    id = request.id
    url = request.url.replace("/api/model-api", "http://model-api")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            body = await response.read()
            file = BytesIO(body)
            image_id = storage_engine.save_file(file, id)
            return {"id": image_id, "url": f"/assets/{image_id}"}


@app.get("/assets/{asset_id}")
async def get_asset(asset_id: UUID):
    asset = storage_engine.get_file(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return StreamingResponse(asset)

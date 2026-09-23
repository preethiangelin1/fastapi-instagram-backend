import uuid
import boto3
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from botocore.config import Config

from config import settings
from auth.oauth2 import CurrentUser
from integrations.s3 import generate_presigned_url
from schemas import PresignRequest, PresignResponse

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

@router.post("/uploads/presign", response_model=PresignResponse)
async def get_presigned_url(
    body: PresignRequest,
    user: CurrentUser,
):
    if body.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, "Unsupported content type")

    ext = ALLOWED_CONTENT_TYPES[body.content_type]
    key = f"posts/{user.id}/{uuid.uuid4()}.{ext}"
    # "posts/5/456hggh-hggh.jpg"

    upload_url = await generate_presigned_url(key, body)

    return PresignResponse(
        upload_url=upload_url,
        key=key,
        cdn_url=f"{settings.cloudfront_domain}/{key}",
    )
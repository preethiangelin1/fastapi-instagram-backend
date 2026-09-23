from io import BytesIO

import boto3
from botocore.config import Config
from fastapi.concurrency import run_in_threadpool
from config import settings

def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=(
            settings.s3_access_key_id.get_secret_value()
            if settings.s3_access_key_id
            else None
        ),
        aws_secret_access_key=(
            settings.s3_secret_access_key.get_secret_value()
            if settings.s3_secret_access_key
            else None
        ),
        endpoint_url=settings.s3_endpoint_url,
        config=Config(signature_version="s3v4")
    )

def _upload_to_s3(file_bytes: bytes, key: str) -> None:
    s3 = _get_s3_client()
    s3.upload_fileobj(
        BytesIO(file_bytes),
        settings.s3_bucket_name,
        key,
        ExtraArgs={"ContentType": "image/jpeg"},
    )

def _delete_from_s3(key: str) -> None:
    s3 = _get_s3_client()
    s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)

def _generate_presigned_url(key, body):
    s3_client = _get_s3_client()
    return s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.s3_bucket_name,
            "Key": key,
            "ContentType": body.content_type,
        },
        ExpiresIn=60,
    )

def _head_object(key: str):
    s3_client = _get_s3_client()
    return s3_client.head_object(Bucket=settings.s3_bucket_name, Key=key)

async def head_object(key: str):
    return await run_in_threadpool(_head_object, key)

async def generate_presigned_url(key, body):
    upload_url = await run_in_threadpool(_generate_presigned_url, key, body)
    return upload_url

async def upload_post_image(file_bytes: bytes, filename: str) -> None:
    key = f"posts/{filename}"
    await run_in_threadpool(_upload_to_s3, file_bytes, key)

async def delete_post_image(filename: str | None) -> None:
    if filename is None:
        return
    key = f"posts/{filename}"
    await run_in_threadpool(_delete_from_s3, key)
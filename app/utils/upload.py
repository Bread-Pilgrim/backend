import asyncio
from functools import partial
from typing import List, Tuple

from supabase import Client, create_client

from app.core.config import Configs
from app.core.exception import UploadImageException

config = Configs()

SUPABASE_BUCKET = config.SUPABASE_BUCKET
SUPABASE_ACCESS_KEY = config.SUPABASE_ACCESS_KEY
SUPABASE_URL = config.SUPABASE_URL

supabase: Client = create_client(
    supabase_url=SUPABASE_URL, supabase_key=SUPABASE_ACCESS_KEY
)


async def upload_multiple_to_supabase_storage(
    files: List[Tuple[bytes, str]],
) -> List[str]:
    """여러 이미지를 Supabase 버킷에 업로드하는 메소드."""

    loop = asyncio.get_event_loop()

    for file_bytes, filename in files:
        # Supabase Storage에 저장될 경로 설정
        path_in_bucket = f"images/{filename}"

        try:
            await loop.run_in_executor(
                None,
                partial(
                    supabase.storage.from_(SUPABASE_BUCKET).upload,
                    path_in_bucket,
                    file_bytes,
                    {"content-type": "image/webp"},
                ),
            )
        except Exception as e:
            raise UploadImageException(f"Error processing {filename}: {e}") from e

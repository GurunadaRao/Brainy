import io
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from src.configs.settings import settings


class S3Client:
    def __init__(self) -> None:
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self._ensure_buckets()

    def _ensure_buckets(self) -> None:
        """Ensure default buckets 'audio-blobs' and 'transcripts' exist."""
        for bucket in ["audio-blobs", "transcripts"]:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    print(f"MinIO: Created bucket '{bucket}'")
            except S3Error as e:
                print(f"MinIO Error initializing bucket '{bucket}': {e}")

    def upload_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        """Upload a file from local disk to a bucket."""
        try:
            self.client.fput_object(bucket_name, object_name, file_path)
        except S3Error as e:
            raise RuntimeError(
                f"Failed to upload {file_path} to {bucket_name}/{object_name}: {e}"
            )

    def upload_stream(
        self, bucket_name: str, object_name: str, data: BinaryIO, length: int
    ) -> None:
        """Upload a binary stream to a bucket."""
        try:
            self.client.put_object(
                bucket_name,
                object_name,
                data,
                length,
                content_type="application/octet-stream",
            )
        except S3Error as e:
            raise RuntimeError(
                f"Failed to upload stream to {bucket_name}/{object_name}: {e}"
            )

    def download_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        """Download a file from a bucket to local disk."""
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
        except S3Error as e:
            raise RuntimeError(
                f"Failed to download {bucket_name}/{object_name} to {file_path}: {e}"
            )

    def get_object(self, bucket_name: str, object_name: str) -> io.BytesIO:
        """Fetch an object directly into memory as a BytesIO stream."""
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = io.BytesIO(response.read())
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise RuntimeError(f"Failed to get object {bucket_name}/{object_name}: {e}")


# Global storage client instance
s3_client = S3Client()

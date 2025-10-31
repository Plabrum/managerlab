import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Annotated

import boto3
from litestar.params import Dependency

from app.utils.configure import Config


class BaseS3Client(ABC):
    """Abstract base class for S3-like operations."""

    @abstractmethod
    def download(self, local_path: str | Path, s3_key: str) -> None:
        """Download file from storage."""
        pass

    @abstractmethod
    def upload(self, local_path: str | Path, s3_key: str) -> None:
        """Upload file to storage."""
        pass

    @abstractmethod
    def upload_fileobj(self, fileobj, s3_key: str) -> None:
        """Upload file-like object to storage."""
        pass

    @abstractmethod
    def generate_presigned_upload_url(self, key: str, content_type: str, expires_in: int = 300) -> str:
        """Generate presigned URL for uploading a file."""
        pass

    @abstractmethod
    def generate_presigned_download_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL for downloading/viewing a file."""
        pass

    @abstractmethod
    def delete_file(self, key: str) -> None:
        """Delete a file from storage."""
        pass

    @abstractmethod
    def file_exists(self, key: str) -> bool:
        """Check if a file exists in storage."""
        pass

    @abstractmethod
    def get_file_bytes(self, key: str) -> bytes:
        """Get file contents as bytes."""
        pass


class LocalS3Client(BaseS3Client):
    """Local filesystem implementation for development."""

    def __init__(self, uploads_dir: str = "uploads"):
        self.uploads_dir = Path(uploads_dir)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def _get_local_storage_path(self, key: str) -> Path:
        """Convert S3 key to local storage path."""
        # Strip leading slash to ensure relative path
        key = key.lstrip("/")
        return self.uploads_dir / key

    def download(self, local_path: str | Path, s3_key: str) -> None:
        """Copy from local storage to target location."""
        local_path = Path(local_path)
        storage_path = self._get_local_storage_path(s3_key)

        local_path.parent.mkdir(parents=True, exist_ok=True)

        if storage_path.exists():
            shutil.copy2(storage_path, local_path)

    def upload(self, local_path: str | Path, s3_key: str) -> None:
        """Copy from local path to storage location."""
        local_path = Path(local_path)
        storage_path = self._get_local_storage_path(s3_key)

        storage_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, storage_path)

    def upload_fileobj(self, fileobj, s3_key: str) -> None:
        """Upload file-like object to storage location."""
        storage_path = self._get_local_storage_path(s3_key)
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(fileobj.read())

    def generate_presigned_upload_url(self, key: str, content_type: str, expires_in: int = 300) -> str:
        """Generate mock presigned URL for local development."""
        # In local mode, return a fake URL that includes the key
        # The frontend can use this to know where to "upload" (store the key)
        return f"http://localhost:8000/local-upload/{key}"

    def generate_presigned_download_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate mock presigned URL for local development."""
        return f"http://localhost:8000/local-download/{key}"

    def delete_file(self, key: str) -> None:
        """Delete file from local storage."""
        storage_path = self._get_local_storage_path(key)
        if storage_path.exists():
            storage_path.unlink()

    def file_exists(self, key: str) -> bool:
        """Check if file exists in local storage."""
        return self._get_local_storage_path(key).exists()

    def get_file_bytes(self, key: str) -> bytes:
        """Get file contents as bytes."""
        return self._get_local_storage_path(key).read_bytes()


class S3Client(BaseS3Client):
    """AWS S3 client implementation."""

    def __init__(self, config: Config):
        self.bucket_name = config.S3_BUCKET
        self.s3 = boto3.client("s3")

    def download(self, local_path: str | Path, s3_key: str) -> None:
        """Download file from S3."""
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self.s3.download_file(self.bucket_name, s3_key, str(local_path))

    def upload(self, local_path: str | Path, s3_key: str) -> None:
        """Upload file to S3."""
        self.s3.upload_file(str(local_path), self.bucket_name, s3_key)

    def upload_fileobj(self, fileobj, s3_key: str) -> None:
        """Upload file-like object to S3."""
        self.s3.upload_fileobj(fileobj, self.bucket_name, s3_key)

    def generate_presigned_upload_url(self, key: str, content_type: str, expires_in: int = 300) -> str:
        """Generate presigned URL for uploading a file to S3."""
        return self.s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

    def generate_presigned_download_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL for downloading/viewing a file from S3."""
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )

    def delete_file(self, key: str) -> None:
        """Delete a file from S3."""
        self.s3.delete_object(Bucket=self.bucket_name, Key=key)

    def file_exists(self, key: str) -> bool:
        """Check if a file exists in S3."""
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def get_file_bytes(self, key: str) -> bytes:
        """Get file contents as bytes from S3."""
        from io import BytesIO

        fileobj = BytesIO()
        self.s3.download_fileobj(self.bucket_name, key, fileobj)
        return fileobj.getvalue()


def provide_s3_client(config: Config) -> BaseS3Client:
    """Factory function to create appropriate S3 client based on config."""
    if config.IS_DEV:
        return LocalS3Client(uploads_dir="uploads")
    else:
        return S3Client(config)


S3Dep = Annotated[BaseS3Client, Dependency()]

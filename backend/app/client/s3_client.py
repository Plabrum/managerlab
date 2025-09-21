import os
import shutil
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Optional

import boto3
from botocore.exceptions import ClientError
from litestar.params import Dependency

from app.config import Config


@dataclass
class S3ObjectMeta:
    """Metadata for an S3 object."""

    last_modified: Optional[datetime]  # timezone-aware UTC
    size: Optional[int]


class BaseS3Client(ABC):
    """Abstract base class for S3-like operations."""

    @abstractmethod
    def download(self, local_path: str | Path, s3_key: str = "nfl_odds.db") -> bool:
        pass

    @abstractmethod
    def upload(self, local_path: str | Path, s3_key: str = "nfl_odds.db") -> None:
        """Upload file to storage."""
        pass

    @abstractmethod
    def _head(self, key: str) -> Optional[S3ObjectMeta]:
        """Get metadata for a storage object."""
        pass


class LocalS3Client(BaseS3Client):
    def __init__(self, uploads_dir: str = "uploads"):
        self.uploads_dir = Path(uploads_dir)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def _get_local_storage_path(self, key: str) -> Path:
        """Convert S3 key to local storage path."""
        return self.uploads_dir / key

    def _head(self, key: str) -> Optional[S3ObjectMeta]:
        """Return local file metadata or None if file not found."""
        storage_path = self._get_local_storage_path(key)

        if not storage_path.exists():
            return None

        stat = storage_path.stat()
        return S3ObjectMeta(
            last_modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            size=stat.st_size,
        )

    def download(self, local_path: str | Path, s3_key: str = "nfl_odds.db") -> bool:
        """Copy from local storage to target location."""
        local_path = Path(local_path)
        storage_path = self._get_local_storage_path(s3_key)

        self._ensure_parent_dir(local_path)

        # Check if source exists in storage
        if not storage_path.exists():
            # Create empty file if nothing in storage
            if not local_path.exists():
                local_path.touch()
            return False

        # Check if we need to copy
        local_mtime = self._get_file_mtime(local_path)
        storage_mtime = self._get_file_mtime(storage_path)

        if local_mtime is None or (storage_mtime and storage_mtime > local_mtime):
            shutil.copy2(storage_path, local_path)
            return True

        return False

    def upload(self, local_path: str | Path, s3_key: str = "nfl_odds.db") -> None:
        """Copy from local path to storage location."""
        local_path = Path(local_path)
        storage_path = self._get_local_storage_path(s3_key)

        self._ensure_parent_dir(storage_path)
        shutil.copy2(local_path, storage_path)

        # Update local file timestamp
        now = time.time()
        os.utime(local_path, (now, now))

    @staticmethod
    def _get_file_mtime(path: Path) -> Optional[datetime]:
        """Get file modification time as UTC datetime."""
        if not path.exists():
            return None
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

    @staticmethod
    def _ensure_parent_dir(path: Path) -> None:
        """Ensure parent directory exists."""
        path.parent.mkdir(parents=True, exist_ok=True)


class S3Client(BaseS3Client):
    """AWS S3 client implementation."""

    def __init__(self, config: Config):
        self.bucket_name = config.S3_BUCKET
        self.s3 = boto3.client("s3")

    def _head(self, key: str) -> Optional[S3ObjectMeta]:
        """Return remote S3 metadata or None if object not found."""
        try:
            resp = self.s3.head_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            # Handle 404/NoSuchKey as missing object
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise  # Re-raise other errors

        return S3ObjectMeta(
            last_modified=resp.get("LastModified"),  # Already timezone-aware
            size=resp.get("ContentLength"),
        )

    def download(self, local_path: str | Path, s3_key: str = "nfl_odds.db") -> bool:
        """Download file from S3 if newer than local version."""
        local_path = Path(local_path)
        self._ensure_parent_dir(local_path)

        # Get remote metadata
        remote_meta = self._head(s3_key)
        if not remote_meta or not remote_meta.last_modified:
            # Nothing to download, ensure local file exists
            if not local_path.exists():
                local_path.touch()
            return False

        # Compare timestamps
        local_mtime = self._get_file_mtime(local_path)
        if local_mtime is None or remote_meta.last_modified > local_mtime:
            # Download and sync timestamps
            self.s3.download_file(self.bucket_name, s3_key, str(local_path))
            self._sync_file_time(local_path, remote_meta.last_modified)
            return True

        return False

    def upload(self, local_path: str | Path, s3_key: str = "nfl_odds.db") -> None:
        """Upload file to S3."""
        local_path = Path(local_path)
        self.s3.upload_file(str(local_path), self.bucket_name, s3_key)

        # Update local timestamp to indicate successful upload
        now = time.time()
        os.utime(local_path, (now, now))

    @staticmethod
    def _get_file_mtime(path: Path) -> Optional[datetime]:
        """Get file modification time as UTC datetime."""
        if not path.exists():
            return None
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

    @staticmethod
    def _ensure_parent_dir(path: Path) -> None:
        """Ensure parent directory exists."""
        path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _sync_file_time(path: Path, remote_time: datetime) -> None:
        """Set local file time to match remote time."""
        timestamp = remote_time.timestamp()
        os.utime(path, (timestamp, timestamp))


def provide_s3_client(config: Config) -> BaseS3Client:
    """Factory function to create appropriate S3 client based on config."""
    if config.IS_DEV:
        return LocalS3Client(uploads_dir="uploads")
    else:
        return S3Client(config)


S3Dep = Annotated[BaseS3Client, Dependency()]

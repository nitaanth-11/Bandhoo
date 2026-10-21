"""
Controlled Private File Storage Abstraction for Bandhoo.

Implements secure storage for uploaded evidence files and generated PDFs:
- Stores files outside of web-accessible roots.
- Prevents path traversal vulnerabilities.
- Generates and verifies SHA-256 cryptographic hashes for integrity.
- Stores storage keys in PostgreSQL rather than filesystem paths.
- Provides atomic writes to prevent partially written files on crash.
"""

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple


class StorageSecurityError(Exception):
    """Raised when a path traversal or security violation is detected."""
    pass


class StorageIntegrityError(Exception):
    """Raised when stored file content does not match its expected SHA-256 hash."""
    pass


class PrivateFileStorage:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.environ.get("BANDHOO_STORAGE_DIR", "private_storage")
        self.base_path = Path(base_dir).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, storage_key: str) -> Path:
        """
        Resolves storage_key against base_path, strictly prohibiting path traversal.
        """
        # Normalize slashes and reject absolute paths or traversal sequences
        clean_key = storage_key.strip().replace("\\", "/").lstrip("/")
        if ".." in clean_key.split("/"):
            raise StorageSecurityError(f"Path traversal attempt detected in key: {storage_key}")

        target_path = (self.base_path / clean_key).resolve()
        if not str(target_path).startswith(str(self.base_path)):
            raise StorageSecurityError(f"Storage path {target_path} escapes root {self.base_path}")

        return target_path

    def save_file(
        self,
        data: bytes,
        storage_key: str,
        expected_sha256: Optional[str] = None
    ) -> Tuple[str, int, str]:
        """
        Atomically saves binary data to private storage under storage_key.
        Returns: (normalized_storage_key, size_bytes, sha256_hash)
        """
        target_path = self._resolve_safe_path(storage_key)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Compute SHA-256 hash
        computed_hash = hashlib.sha256(data).hexdigest()
        if expected_sha256 and expected_sha256.lower() != computed_hash.lower():
            raise StorageIntegrityError(
                f"Payload hash {computed_hash} does not match expected {expected_sha256}"
            )

        file_size = len(data)

        # Atomic write via temporary file
        temp_dir = target_path.parent
        with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False) as tmp_f:
            tmp_f.write(data)
            tmp_path = Path(tmp_f.name)

        try:
            shutil.move(str(tmp_path), str(target_path))
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise

        # Return standardized forward-slash relative storage key
        normalized_key = storage_key.strip().replace("\\", "/").lstrip("/")
        return normalized_key, file_size, computed_hash

    def read_file(self, storage_key: str, verify_sha256: Optional[str] = None) -> bytes:
        """
        Reads binary file from private storage, with optional SHA-256 validation.
        """
        target_path = self._resolve_safe_path(storage_key)
        if not target_path.exists() or not target_path.is_file():
            raise FileNotFoundError(f"Storage key not found: {storage_key}")

        data = target_path.read_bytes()
        if verify_sha256:
            current_hash = hashlib.sha256(data).hexdigest()
            if current_hash.lower() != verify_sha256.lower():
                raise StorageIntegrityError(
                    f"Integrity check failed for {storage_key}: expected {verify_sha256}, got {current_hash}"
                )
        return data

    def exists(self, storage_key: str) -> bool:
        """Checks if a storage key exists in private storage."""
        try:
            target_path = self._resolve_safe_path(storage_key)
            return target_path.exists() and target_path.is_file()
        except StorageSecurityError:
            return False

    def delete_file(self, storage_key: str) -> bool:
        """Deletes a file from private storage."""
        target_path = self._resolve_safe_path(storage_key)
        if target_path.exists() and target_path.is_file():
            target_path.unlink()
            return True
        return False


# Default singleton instance
default_storage = PrivateFileStorage()

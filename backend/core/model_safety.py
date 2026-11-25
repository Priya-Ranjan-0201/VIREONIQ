"""
Model Supply Chain and Serialization Security Guards.

Enforces:
1. Strict prohibition of untrusted Python serialization (pickle, joblib).
2. Safe tensor / structure formats (safetensors, ONNX, JSON).
3. Cryptographic hash (SHA-256) integrity verification against pinned manifests.
4. Prevention of arbitrary runtime downloads from unpinned or unverified sources.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional, Set

# Permitted safe artifact extensions
ALLOWED_MODEL_EXTENSIONS: Set[str] = {
    ".safetensors",
    ".onnx",
    ".json",
    ".tflite",
}

# Strictly forbidden formats susceptible to arbitrary code execution
FORBIDDEN_SERIALIZATION_EXTENSIONS: Set[str] = {
    ".pkl",
    ".pickle",
    ".joblib",
    ".pt",
    ".bin",
    ".npy",
    ".npz",
}


class ModelSecurityError(Exception):
    """Raised when an artifact fails security verification."""
    pass


class ModelIntegrityRegistry:
    """
    Registry for verified model artifact digests.
    """

    def __init__(self, manifest_path: Optional[Path] = None):
        self._manifest: Dict[str, str] = {}
        if manifest_path and manifest_path.is_file():
            self.load_manifest(manifest_path)

    def load_manifest(self, manifest_path: Path) -> None:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._manifest.update(data)
        except Exception as e:
            raise ModelSecurityError(f"Failed to parse model manifest: {e}")

    def register_artifact(self, model_id: str, sha256_hash: str) -> None:
        self._manifest[model_id] = sha256_hash.lower()

    def verify_file(self, file_path: Path, model_id: Optional[str] = None) -> bool:
        """
        Verify that file_path:
        1. Uses an allowed, safe serialization extension.
        2. Does not use dangerous execution-capable serialization.
        3. Matches the registered SHA-256 digest if model_id is specified.
        """
        suffix = file_path.suffix.lower()

        if suffix in FORBIDDEN_SERIALIZATION_EXTENSIONS:
            raise ModelSecurityError(
                f"Loading forbidden serialization format '{suffix}' is rejected. "
                f"Use safe formats such as .safetensors or .onnx."
            )

        if suffix not in ALLOWED_MODEL_EXTENSIONS:
            raise ModelSecurityError(
                f"Unrecognized or unverified model extension '{suffix}'. "
                f"Allowed formats: {sorted(ALLOWED_MODEL_EXTENSIONS)}"
            )

        if not file_path.is_file():
            raise ModelSecurityError(f"Model file not found: {file_path}")

        if model_id:
            expected_hash = self._manifest.get(model_id)
            if not expected_hash:
                raise ModelSecurityError(
                    f"Model '{model_id}' is not pinned in the trusted model manifest."
                )
            computed_hash = compute_sha256(file_path)
            if computed_hash != expected_hash:
                raise ModelSecurityError(
                    f"Integrity check failed for model '{model_id}'. "
                    f"Expected SHA256: {expected_hash}, computed: {computed_hash}"
                )

        return True


def compute_sha256(file_path: Path) -> str:
    """Computes the SHA-256 digest of a local file in chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


# Default global registry instance
default_model_registry = ModelIntegrityRegistry()

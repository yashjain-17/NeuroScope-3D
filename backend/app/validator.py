"""
Input validation for NeuroScope 3D.
Checks NIfTI integrity, dimensions, finite values, file size and modality alignment.
"""

import hashlib
import os
from typing import Dict, Tuple

import nibabel as nib
import numpy as np

from .config import MAX_FILE_SIZE_BYTES, REQUIRED_MODALITIES


class ValidationError(Exception):
    """Raised when an input scan fails validation."""

    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 in bounded memory for audit provenance."""
    digest = hashlib.sha256()
    with open(file_path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_file_size(file_path: str) -> None:
    """Reject files larger than the configured upload limit."""
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(
            code="FILE_TOO_LARGE",
            message=(
                f"File exceeds the maximum allowed size of "
                f"{MAX_FILE_SIZE_BYTES / (1024 ** 3):.2f} GB "
                f"({file_size / (1024 ** 3):.2f} GB received)."
            ),
        )


def validate_single_nifti(
    file_path: str,
) -> Tuple[nib.Nifti1Image, np.ndarray, np.ndarray, Tuple[float, ...]]:
    """Load and validate one 3D NIfTI scan."""
    check_file_size(file_path)

    try:
        image = nib.load(file_path)
        data = image.get_fdata(dtype=np.float32)
    except Exception as exc:
        raise ValidationError(
            code="CORRUPT_NIFTI",
            message=f"Failed to parse NIfTI file: {exc}",
        ) from exc

    if data.ndim != 3:
        raise ValidationError(
            code="UNSUPPORTED_DIMENSIONS",
            message=f"Expected a 3D volume, received {data.ndim}D data.",
        )
    if not np.isfinite(data).all():
        raise ValidationError(
            code="NONFINITE_VALUES",
            message="Volume contains non-finite values (NaN or Inf).",
        )
    if not np.any(data) or float(np.std(data)) == 0.0:
        raise ValidationError(
            code="CONSTANT_VOLUME",
            message="Volume is constant or contains only zero voxels.",
        )

    return image, data, image.affine, image.header.get_zooms()[:3]


def check_skull_stripped(data: np.ndarray) -> bool:
    """Estimate skull stripping from non-zero values on all six volume faces."""
    border_voxels = np.concatenate(
        [
            data[0, :, :].ravel(),
            data[-1, :, :].ravel(),
            data[:, 0, :].ravel(),
            data[:, -1, :].ravel(),
            data[:, :, 0].ravel(),
            data[:, :, -1].ravel(),
        ]
    )
    if border_voxels.size == 0:
        return False
    non_zero_ratio = np.count_nonzero(border_voxels) / float(border_voxels.size)
    return non_zero_ratio < 0.05


def validate_study_set(file_paths: Dict[str, str]) -> Dict[str, object]:
    """Validate all required modalities and their spatial alignment."""
    missing = [mod for mod in REQUIRED_MODALITIES if not file_paths.get(mod)]
    if missing:
        raise ValidationError(
            code="MISSING_SEQUENCE",
            message=f"Missing required modality sequence(s): {', '.join(missing).upper()}.",
        )

    images = {}
    data_by_modality = {}
    hashes = []

    for modality in REQUIRED_MODALITIES:
        image, data, affine, _zooms = validate_single_nifti(file_paths[modality])
        images[modality] = (image, affine)
        data_by_modality[modality] = data
        hashes.append(compute_sha256(file_paths[modality]))

    reference_image, reference_affine = images["t1"]
    reference_shape = data_by_modality["t1"].shape

    for modality in REQUIRED_MODALITIES:
        if data_by_modality[modality].shape != reference_shape:
            raise ValidationError(
                code="SHAPE_MISMATCH",
                message=(
                    f"{modality.upper()} shape {data_by_modality[modality].shape} "
                    f"does not match T1 shape {reference_shape}."
                ),
            )
        if not np.allclose(images[modality][1], reference_affine, atol=1e-3):
            raise ValidationError(
                code="AFFINE_MISMATCH",
                message=f"Affine coordinate mismatch between {modality.upper()} and T1.",
            )

    combined_hash = hashlib.sha256("".join(hashes).encode("utf-8")).hexdigest()
    return {
        "valid": True,
        "ref_shape": reference_shape,
        "ref_affine": reference_affine,
        "zooms": reference_image.header.get_zooms()[:3],
        "is_skull_stripped": check_skull_stripped(data_by_modality["t1"]),
        "combined_hash": combined_hash,
    }

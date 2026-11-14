"""
MONAI model inference engine for NeuroScope 3D.

IMPORTANT: inference is disabled until a trained, compatible checkpoint is
explicitly configured. Randomly initialized network weights must never be
presented as a tumour segmentation.
"""

import os
import time
from pathlib import Path
from typing import Dict, Tuple

import nibabel as nib
import numpy as np
import torch

from .config import LABEL_ED, LABEL_ET, LABEL_NCR

_MODEL_CACHE = None
_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _checkpoint_state_dict(checkpoint):
    """Accept a raw state_dict or a common checkpoint wrapper."""
    if not isinstance(checkpoint, dict):
        raise RuntimeError("Model checkpoint must contain a state dictionary.")

    for key in ("state_dict", "model_state_dict", "model"):
        value = checkpoint.get(key)
        if isinstance(value, dict):
            checkpoint = value
            break

    # Remove a common DataParallel prefix without changing other parameter names.
    if checkpoint and all(key.startswith("module.") for key in checkpoint):
        checkpoint = {key.removeprefix("module."): value for key, value in checkpoint.items()}

    if not checkpoint or not all(isinstance(key, str) for key in checkpoint):
        raise RuntimeError("Checkpoint does not contain valid model parameters.")
    return checkpoint


def load_monai_model():
    """Load a trained MONAI SegResNet checkpoint; fail closed if unavailable."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    checkpoint_value = os.getenv("NEUROSCOPE_MODEL_CHECKPOINT", "").strip()
    if not checkpoint_value:
        raise RuntimeError(
            "Segmentation is disabled: set NEUROSCOPE_MODEL_CHECKPOINT to a "
            "validated, trained SegResNet checkpoint. No random-weight inference is allowed."
        )

    checkpoint_path = Path(checkpoint_value).expanduser().resolve()
    if not checkpoint_path.is_file():
        raise RuntimeError(f"Configured model checkpoint was not found: {checkpoint_path}")

    try:
        from monai.networks.nets import SegResNet

        model = SegResNet(
            spatial_dims=3,
            in_channels=4,
            out_channels=3,
            init_filters=16,
            blocks_down=[1, 2, 2, 4],
            blocks_up=[1, 1, 1],
        )

        try:
            checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        except TypeError:
            # Compatibility with older supported PyTorch versions.
            checkpoint = torch.load(checkpoint_path, map_location="cpu")

        state_dict = _checkpoint_state_dict(checkpoint)
        model.load_state_dict(state_dict, strict=True)
        model = model.to(_DEVICE)
        model.eval()
        _MODEL_CACHE = model
        return model
    except Exception as exc:
        raise RuntimeError(
            f"Unable to load a compatible trained SegResNet checkpoint: {exc}"
        ) from exc


def convert_nested_masks_to_brats_codes(
    tc_mask: np.ndarray, wt_mask: np.ndarray, et_mask: np.ndarray
) -> np.ndarray:
    """Convert nested TC/WT/ET masks to BraTS labels (NCR=1, ED=2, ET=4)."""
    if tc_mask.shape != wt_mask.shape or tc_mask.shape != et_mask.shape:
        raise ValueError("TC, WT and ET masks must have identical shapes.")

    # Enforce the expected nesting before assigning mutually exclusive labels.
    et_mask = np.logical_and(et_mask, tc_mask)
    tc_mask = np.logical_and(tc_mask, wt_mask)
    ed_mask = np.logical_and(wt_mask, np.logical_not(tc_mask))
    ncr_mask = np.logical_and(tc_mask, np.logical_not(et_mask))

    brats_map = np.zeros(wt_mask.shape, dtype=np.int16)
    brats_map[ed_mask] = LABEL_ED
    brats_map[ncr_mask] = LABEL_NCR
    brats_map[et_mask] = LABEL_ET
    return brats_map


def run_inference(file_paths: Dict[str, str], output_save_path: str) -> Tuple[np.ndarray, float]:
    """Run inference only with the explicitly configured trained checkpoint."""
    start_time = time.time()

    required = ("t1gd", "t1", "t2", "flair")
    missing = [name for name in required if not file_paths.get(name)]
    if missing:
        raise ValueError(f"Missing required modality paths: {', '.join(missing)}")

    images = {name: nib.load(file_paths[name]) for name in required}
    reference = images["t1"]
    reference_shape = reference.shape
    reference_affine = reference.affine

    modality_arrays = []
    for name in required:
        image = images[name]
        if image.shape != reference_shape:
            raise ValueError(
                f"{name.upper()} shape {image.shape} does not match T1 shape {reference_shape}."
            )
        if not np.allclose(image.affine, reference_affine, atol=1e-3):
            raise ValueError(f"{name.upper()} affine does not match T1 coordinates.")

        data = image.get_fdata(dtype=np.float32)
        if data.ndim != 3 or not np.isfinite(data).all():
            raise ValueError(f"{name.upper()} must be a finite 3D volume.")

        foreground = data > 0
        if np.any(foreground):
            mean = float(np.mean(data[foreground]))
            std = float(np.std(data[foreground]))
            data[foreground] = (data[foreground] - mean) / max(std, 1e-8)
        modality_arrays.append(data)

    input_tensor = torch.from_numpy(np.stack(modality_arrays, axis=0)).unsqueeze(0).to(_DEVICE)
    model = load_monai_model()

    from monai.inferers import sliding_window_inference

    with torch.inference_mode():
        output_logits = sliding_window_inference(
            inputs=input_tensor,
            roi_size=(128, 128, 128),
            sw_batch_size=2,
            predictor=model,
            overlap=0.5,
        )
        probs = torch.sigmoid(output_logits).squeeze(0).cpu().numpy()

    tc_mask = probs[0] > 0.5
    wt_mask = probs[1] > 0.5
    et_mask = probs[2] > 0.5
    pred_label_map = convert_nested_masks_to_brats_codes(tc_mask, wt_mask, et_mask)

    output_nifti = nib.Nifti1Image(pred_label_map, affine=reference.affine, header=reference.header)
    nib.save(output_nifti, output_save_path)

    return pred_label_map, round(time.time() - start_time, 2)

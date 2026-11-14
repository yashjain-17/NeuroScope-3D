import numpy as np
import pytest

from app.inference import convert_nested_masks_to_brats_codes


def test_nested_masks_map_to_brats_labels():
    wt = np.array([1, 1, 1, 0], dtype=bool)
    tc = np.array([1, 1, 0, 0], dtype=bool)
    et = np.array([1, 0, 0, 0], dtype=bool)

    result = convert_nested_masks_to_brats_codes(tc, wt, et)

    np.testing.assert_array_equal(result, np.array([4, 1, 2, 0], dtype=np.int16))


def test_non_nested_predictions_are_intersected_safely():
    wt = np.array([1, 0], dtype=bool)
    tc = np.array([1, 1], dtype=bool)
    et = np.array([1, 1], dtype=bool)

    result = convert_nested_masks_to_brats_codes(tc, wt, et)

    np.testing.assert_array_equal(result, np.array([4, 0], dtype=np.int16))


def test_mismatched_mask_shapes_are_rejected():
    with pytest.raises(ValueError, match="identical shapes"):
        convert_nested_masks_to_brats_codes(
            np.zeros((2, 2), dtype=bool),
            np.zeros((2, 2), dtype=bool),
            np.zeros((3, 2), dtype=bool),
        )

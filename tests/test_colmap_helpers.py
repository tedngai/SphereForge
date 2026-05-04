"""Tests for sphereforge.common.colmap_helpers.

Covers quaternion↔rotation-matrix conversions and COLMAP text parsers.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from sphereforge.common.colmap_helpers import (
    quat_to_rotation_matrix,
    rotation_matrix_to_quat,
)


class TestRotationMatrixToQuat:
    """Unit tests for rotation_matrix_to_quat using known ground-truth rotations."""

    def test_identity(self) -> None:
        """Identity matrix → identity quaternion (1, 0, 0, 0)."""
        R = np.eye(3, dtype=np.float64)
        qw, qx, qy, qz = rotation_matrix_to_quat(R)
        assert qw == pytest.approx(1.0, abs=1e-10)
        assert qx == pytest.approx(0.0, abs=1e-10)
        assert qy == pytest.approx(0.0, abs=1e-10)
        assert qz == pytest.approx(0.0, abs=1e-10)

    @pytest.mark.parametrize(
        ("axis", "expected"),
        [
            # 90° about X
            (
                np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=np.float64),
                (1 / math.sqrt(2), 1 / math.sqrt(2), 0.0, 0.0),
            ),
            # 90° about Y
            (
                np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], dtype=np.float64),
                (1 / math.sqrt(2), 0.0, 1 / math.sqrt(2), 0.0),
            ),
            # 90° about Z
            (
                np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=np.float64),
                (1 / math.sqrt(2), 0.0, 0.0, 1 / math.sqrt(2)),
            ),
            # 180° about X
            (
                np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=np.float64),
                (0.0, 1.0, 0.0, 0.0),
            ),
            # 180° about Y
            (
                np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]], dtype=np.float64),
                (0.0, 0.0, 1.0, 0.0),
            ),
            # 180° about Z
            (
                np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]], dtype=np.float64),
                (0.0, 0.0, 0.0, 1.0),
            ),
        ],
    )
    def test_known_rotations(
        self, axis: np.ndarray, expected: tuple[float, float, float, float]
    ) -> None:
        """rotation_matrix_to_quat matches known analytical results."""
        qw, qx, qy, qz = rotation_matrix_to_quat(axis)
        # Quaternions q and -q represent the same rotation.  Ensure qw is
        # non-negative (canonical form) before comparing.
        if qw < 0:
            qw, qx, qy, qz = -qw, -qx, -qy, -qz
        assert qw == pytest.approx(expected[0], abs=1e-10)
        assert qx == pytest.approx(expected[1], abs=1e-10)
        assert qy == pytest.approx(expected[2], abs=1e-10)
        assert qz == pytest.approx(expected[3], abs=1e-10)

    def test_roundtrip_random(self) -> None:
        """quat → R → quat is identity for random unit quaternions."""
        rng = np.random.default_rng(42)
        for _ in range(50):
            q = rng.normal(size=4)
            q = q / np.linalg.norm(q)
            R = quat_to_rotation_matrix(*q)
            qw2, qx2, qy2, qz2 = rotation_matrix_to_quat(R)
            # Same rotation → q or -q
            dot = q[0] * qw2 + q[1] * qx2 + q[2] * qy2 + q[3] * qz2
            assert abs(abs(dot) - 1.0) < 1e-9

    def test_non_3x3_raises(self) -> None:
        """Non-3x3 matrix raises ValueError."""
        with pytest.raises(ValueError, match="Expected 3x3"):
            rotation_matrix_to_quat(np.eye(4))

    def test_orthogonal_property(self) -> None:
        """Output quaternion has unit norm."""
        rng = np.random.default_rng(7)
        for _ in range(20):
            q = rng.normal(size=4)
            q = q / np.linalg.norm(q)
            R = quat_to_rotation_matrix(*q)
            qw, qx, qy, qz = rotation_matrix_to_quat(R)
            norm = math.sqrt(qw * qw + qx * qx + qy * qy + qz * qz)
            assert norm == pytest.approx(1.0, abs=1e-10)


class TestQuatToRotationMatrix:
    """Unit tests for quat_to_rotation_matrix."""

    def test_zero_quaternion_raises(self) -> None:
        """Zero quaternion raises ValueError."""
        with pytest.raises(ValueError, match="near-zero norm"):
            quat_to_rotation_matrix(0.0, 0.0, 0.0, 0.0)

    def test_rotation_matrix_orthogonal(self) -> None:
        """R @ R.T ≈ I for random quaternions."""
        rng = np.random.default_rng(13)
        for _ in range(20):
            q = rng.normal(size=4)
            q = q / np.linalg.norm(q)
            R = quat_to_rotation_matrix(*q)
            np.testing.assert_allclose(
                R @ R.T, np.eye(3), atol=1e-12, rtol=1e-12
            )
            np.testing.assert_allclose(
                np.linalg.det(R), 1.0, atol=1e-12, rtol=1e-12
            )

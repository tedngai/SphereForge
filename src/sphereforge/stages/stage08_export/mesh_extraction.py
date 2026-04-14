"""SphereForge Stage 8: Navigation mesh extraction.

Optional module for extracting a mesh from Gaussian positions.
Uses Poisson reconstruction (Open3D), marching cubes (scikit-image),
or convex hull (scipy) as fallbacks.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def extract_navigation_mesh(
    positions: np.ndarray,
    output_path: Path,
    method: str = "poisson",
) -> Path:
    """Extract a navigation mesh from Gaussian positions.

    Tries multiple methods in order of preference:
    1. Poisson reconstruction (requires Open3D)
    2. Marching cubes on a voxel grid (requires scikit-image)
    3. Convex hull (requires scipy — always available)

    Args:
        positions: (N, 3) float32 Gaussian positions.
        output_path: Output OBJ file path.
        method: "poisson", "marching_cubes", or "convex_hull".

    Returns:
        Path to the written OBJ file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if method == "poisson":
        try:
            return _poisson_reconstruction(positions, output_path)
        except ImportError:
            logger.warning("Open3D not installed, falling back to marching cubes")
            method = "marching_cubes"

    if method == "marching_cubes":
        try:
            return _marching_cubes(positions, output_path)
        except ImportError:
            logger.warning("scikit-image not installed, falling back to convex hull")
            method = "convex_hull"

    if method == "convex_hull":
        return _convex_hull(positions, output_path)

    raise ValueError(f"Unknown mesh extraction method: {method}")


def _poisson_reconstruction(positions: np.ndarray, output_path: Path) -> Path:
    """Extract mesh via Poisson reconstruction using Open3D."""
    import open3d as o3d

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(positions)
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)

    # Write as OBJ
    o3d.io.write_triangle_mesh(str(output_path), mesh)
    logger.info("Poisson mesh extracted: %s (%d triangles)", output_path, len(mesh.triangles))
    return output_path


def _marching_cubes(positions: np.ndarray, output_path: Path) -> Path:
    """Extract mesh via marching cubes on a voxelized density grid."""
    from skimage.measure import marching_cubes

    # Voxelized density grid
    voxel_size = _estimate_voxel_size(positions)
    grid, origin = _voxelize(positions, voxel_size)

    # Run marching cubes
    verts, faces, normals, _ = marching_cubes(grid, level=0.5)

    # Transform from grid coords back to world coords
    verts = verts * voxel_size + origin

    # Write as OBJ
    _write_obj(output_path, verts, faces)
    n_faces = faces.shape[0]
    logger.info("Marching cubes mesh extracted: %s (%d triangles)", output_path, n_faces)
    return output_path


def _convex_hull(positions: np.ndarray, output_path: Path) -> Path:
    """Extract mesh as convex hull using scipy."""
    from scipy.spatial import ConvexHull

    hull = ConvexHull(positions)

    # Write as OBJ
    _write_obj(output_path, positions, hull.simplices)
    logger.info("Convex hull mesh extracted: %s (%d triangles)", output_path, len(hull.simplices))
    return output_path


def _estimate_voxel_size(positions: np.ndarray) -> float:
    """Estimate a reasonable voxel size from point cloud extent."""
    extent = positions.max(axis=0) - positions.min(axis=0)
    max_extent = extent.max()
    # Target ~64 voxels along the longest axis
    return max(max_extent / 64.0, 1e-4)


def _voxelize(positions: np.ndarray, voxel_size: float) -> tuple[np.ndarray, np.ndarray]:
    """Convert point positions to a voxelized density grid.

    Args:
        positions: (N, 3) positions.
        voxel_size: Size of each voxel.

    Returns:
        Tuple of (density_grid, origin). Grid values are float32 density [0, 1].
    """
    mins = positions.min(axis=0)
    maxs = positions.max(axis=0) + voxel_size  # Include max point
    origin = mins

    dims = ((maxs - mins) / voxel_size).astype(int) + 1
    dims = np.clip(dims, 2, 256)  # Cap grid size

    grid = np.zeros(dims, dtype=np.float32)

    # Bin each point into the grid with Gaussian splat
    for pos in positions:
        idx = ((pos - origin) / voxel_size).astype(int)
        idx = np.clip(idx, 0, dims - 1)
        grid[idx[0], idx[1], idx[2]] += 1.0

    # Normalize to [0, 1]
    max_val = grid.max()
    if max_val > 0:
        grid /= max_val

    # Smooth with simple box filter
    from scipy.ndimage import uniform_filter
    grid = uniform_filter(grid, size=2)

    return grid, origin


def _write_obj(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    """Write a simple OBJ file.

    Args:
        path: Output file path.
        vertices: (V, 3) vertex positions.
        faces: (F, 3) triangle face indices (0-indexed).
    """
    with open(path, "w") as f:
        f.write("# SphereForge navigation mesh\n")
        f.write(f"# Vertices: {vertices.shape[0]}, Faces: {faces.shape[0]}\n\n")

        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")

        f.write("\n")

        # OBJ faces are 1-indexed
        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

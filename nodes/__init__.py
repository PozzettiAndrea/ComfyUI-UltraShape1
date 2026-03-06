"""UltraShape ComfyUI nodes package.

This package contains all UltraShape node implementations:
- loader.py: Model and mesh loading nodes
- refine.py: Mesh refinement node
- mesh_io.py: File selection and saving nodes
- wrappers.py: Wrapper classes for data types
- common.py: Shared utilities and constants
- ultrashape/: Vendored UltraShape library
"""

import os
import sys

# Add nodes/ directory to sys.path so 'ultrashape' and 'wrappers' are importable
# This is needed for pickle deserialization across process boundaries
NODES_DIR = os.path.dirname(os.path.abspath(__file__))
if NODES_DIR not in sys.path:
    sys.path.insert(0, NODES_DIR)

# Import node classes (using absolute imports since NODES_DIR is in sys.path)
from loader import UltraShapeLoadModel, UltraShapeLoadCoarseMesh, UltraShapeLoadCoarseMeshFromTrimesh
from refine import UltraShapeRefine
from mesh_io import (
    UltraShapeMeshSelector, UltraShapeSaveGLB, UltraShapeConvertToGLB,
    UltraShapeLoadMesh, UltraShapeSaveMesh, UltraShapeOutputToTrimesh,
)

# Node registration
NODE_CLASS_MAPPINGS = {
    "UltraShapeLoadModel": UltraShapeLoadModel,
    "UltraShapeMeshSelector": UltraShapeMeshSelector,
    "UltraShapeLoadCoarseMesh": UltraShapeLoadCoarseMesh,
    "UltraShapeLoadCoarseMeshFromTrimesh": UltraShapeLoadCoarseMeshFromTrimesh,
    "UltraShapeLoadMesh": UltraShapeLoadMesh,
    "UltraShapeSaveMesh": UltraShapeSaveMesh,
    "UltraShapeOutputToTrimesh": UltraShapeOutputToTrimesh,
    "UltraShapeRefine": UltraShapeRefine,
    "UltraShapeSaveGLB": UltraShapeSaveGLB,
    "UltraShapeConvertToGLB": UltraShapeConvertToGLB,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UltraShapeLoadModel": "UltraShape Load Model",
    "UltraShapeMeshSelector": "UltraShape Mesh Selector",
    "UltraShapeLoadCoarseMesh": "UltraShape Load Coarse Mesh",
    "UltraShapeLoadCoarseMeshFromTrimesh": "UltraShape Load Coarse Mesh From Trimesh",
    "UltraShapeLoadMesh": "UltraShape Load Mesh",
    "UltraShapeSaveMesh": "UltraShape Save Mesh",
    "UltraShapeOutputToTrimesh": "UltraShape Output To Trimesh",
    "UltraShapeRefine": "UltraShape Refine",
    "UltraShapeSaveGLB": "UltraShape Save GLB/OBJ",
    "UltraShapeConvertToGLB": "UltraShape Convert To GLB/OBJ",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]

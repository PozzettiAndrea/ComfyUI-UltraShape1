"""UltraShape mesh IO nodes (file selection and saving)."""

import os
import uuid
from io import BytesIO

from common import COMFY_OUTPUT_DIR, get_timestamp
from wrappers import UltraShapeOutputWrapper

try:
    import folder_paths
except ImportError:
    folder_paths = None

try:
    from comfy_api.latest import Types
except ImportError:
    Types = None


class UltraShapeMeshSelector:
    """Upload and select mesh file.

    Provides file upload functionality for mesh files.
    Upload files to ComfyUI/input/ directory and select them.
    Outputs a relative path string that can be connected to UltraShape Load Coarse Mesh.

    Supported formats: .glb, .gltf, .obj, .ply, .stl
    """

    MESH_EXTENSIONS = [".glb", ".gltf", ".obj", ".ply", ".stl"]

    @classmethod
    def INPUT_TYPES(s):
        # Scan for mesh files in input directory
        files = []

        if folder_paths:
            input_dir = folder_paths.get_input_directory()
            if os.path.exists(input_dir):
                for root, dirs, filenames in os.walk(input_dir):
                    for f in filenames:
                        if any(f.lower().endswith(ext) for ext in s.MESH_EXTENSIONS):
                            full_path = os.path.join(root, f)
                            rel_path = os.path.relpath(full_path, input_dir)
                            files.append(rel_path.replace("\\", "/"))

        files.sort()

        if not files:
            files = ["(upload a mesh file)"]

        return {
            "required": {
                # Use "image" as parameter name with image_upload to enable upload button
                "image": (files, {"image_upload": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("mesh_path",)
    FUNCTION = "select"
    CATEGORY = "UltraShape/Loaders"

    @classmethod
    def IS_CHANGED(s, image):
        if not folder_paths or image == "(upload a mesh file)":
            return float("nan")
        image_path = folder_paths.get_annotated_filepath(image)
        if os.path.exists(image_path):
            return os.path.getmtime(image_path)
        return float("nan")

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if image == "(upload a mesh file)":
            return "Please upload a mesh file (.glb, .obj, .ply, .stl)"
        if folder_paths and not folder_paths.exists_annotated_filepath(image):
            return f"Mesh file not found: {image}"
        return True

    def select(self, image):
        if image == "(upload a mesh file)":
            raise ValueError("Please upload a mesh file first.")

        # Return path with input/ prefix so UltraShapeLoadCoarseMesh can resolve it
        output_path = f"input/{image}"
        print(f"[UltraShape] Selected mesh: {output_path}")
        return (output_path,)


class UltraShapeSaveGLB:
    """Save refined mesh as GLB file"""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mesh": ("TRIMESH",),
            },
            "optional": {
                "output_dir": ("STRING", {"default": "ultrashape_output"}),
                "filename_prefix": ("STRING", {"default": "refined"}),
                "file_format": (["glb", "obj", "ply", "stl"], {"default": "glb"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "save"
    CATEGORY = "UltraShape"
    OUTPUT_NODE = True

    def save(self, mesh, output_dir="ultrashape_output",
             filename_prefix="refined", file_format="glb"):
        out_dir = os.path.join(COMFY_OUTPUT_DIR, output_dir)
        os.makedirs(out_dir, exist_ok=True)

        ts = get_timestamp()
        uid = str(uuid.uuid4())[:8]
        filename = f"{filename_prefix}_{ts}_{uid}.{file_format}"
        save_path = os.path.join(out_dir, filename)

        # Export mesh (trimesh object)
        mesh.export(save_path)

        print(f"[UltraShape] Saved: {save_path}")

        # Return relative path
        rel_path = os.path.relpath(save_path, COMFY_OUTPUT_DIR)
        return (rel_path,)


class UltraShapeConvertToGLB:
    """Convert ULTRASHAPE_OUTPUT to FILE_3D for 3D viewer display."""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "refined_mesh": ("ULTRASHAPE_OUTPUT",),
                "file_format": (["glb", "obj", "stl"], {"default": "glb"}),
            },
        }

    RETURN_TYPES = ("FILE_3D",)
    RETURN_NAMES = ("mesh",)
    FUNCTION = "execute"
    CATEGORY = "UltraShape"

    def execute(self, refined_mesh, file_format):
        buf = BytesIO()
        refined_mesh.mesh.export(buf, file_type=file_format)
        return (Types.File3D(buf, file_format=file_format),)


class UltraShapeLoadMesh:
    """Load a mesh file (.glb/.obj/.ply/.stl) as a TRIMESH object.

    Outputs TRIMESH, which is compatible with Trellis2 nodes and can be fed
    into UltraShape Load Coarse Mesh From Trimesh.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "path": ("STRING", {"default": "input.glb",
                    "tooltip": "Absolute path or path relative to ComfyUI root (e.g. input/mesh.glb)"}),
            }
        }

    RETURN_TYPES = ("TRIMESH",)
    RETURN_NAMES = ("mesh",)
    FUNCTION = "load"
    CATEGORY = "UltraShape/Loaders"

    def load(self, path):
        import trimesh as tm

        if not os.path.isabs(path):
            comfy_root = os.path.dirname(COMFY_OUTPUT_DIR)
            resolved = os.path.normpath(os.path.join(comfy_root, path))
        else:
            resolved = path

        if not os.path.exists(resolved):
            raise FileNotFoundError(f"[UltraShape] Mesh file not found: {resolved}")

        print(f"[UltraShape] Loading mesh from: {resolved}")
        mesh = tm.load(resolved, force="mesh", merge_primitives=True)
        return (mesh,)


class UltraShapeSaveMesh:
    """Save a TRIMESH object to a file in the output directory."""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mesh": ("TRIMESH",),
            },
            "optional": {
                "output_dir": ("STRING", {"default": "ultrashape_output"}),
                "filename_prefix": ("STRING", {"default": "mesh"}),
                "file_format": (["glb", "obj", "ply", "stl"], {"default": "glb"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "save"
    CATEGORY = "UltraShape"
    OUTPUT_NODE = True

    def save(self, mesh, output_dir="ultrashape_output", filename_prefix="mesh", file_format="glb"):
        out_dir = os.path.join(COMFY_OUTPUT_DIR, output_dir)
        os.makedirs(out_dir, exist_ok=True)

        ts = get_timestamp()
        uid = str(uuid.uuid4())[:8]
        filename = f"{filename_prefix}_{ts}_{uid}.{file_format}"
        save_path = os.path.join(out_dir, filename)

        mesh.export(save_path, file_type=file_format)
        print(f"[UltraShape] Saved TRIMESH: {save_path}")

        rel_path = os.path.relpath(save_path, COMFY_OUTPUT_DIR)
        return (rel_path,)


class UltraShapeOutputToTrimesh:
    """Convert ULTRASHAPE_OUTPUT to TRIMESH.

    Allows the refined mesh from UltraShape Refine to flow into
    Trellis2 nodes or UltraShape Save Mesh.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "refined_mesh": ("ULTRASHAPE_OUTPUT",),
            }
        }

    RETURN_TYPES = ("TRIMESH",)
    RETURN_NAMES = ("trimesh",)
    FUNCTION = "convert"
    CATEGORY = "UltraShape"

    def convert(self, refined_mesh):
        mesh = refined_mesh.mesh
        print(f"[UltraShape] Converted ULTRASHAPE_OUTPUT to TRIMESH "
              f"(vertices={len(mesh.vertices)}, faces={len(mesh.faces)})")
        return (mesh,)

from pathlib import Path
from comfy_env import setup_env, copy_files

setup_env()

SCRIPT_DIR = Path(__file__).resolve().parent
COMFYUI_DIR = SCRIPT_DIR.parent.parent

# Copy 1.glb to input/3d/
copy_files(SCRIPT_DIR / "assets", COMFYUI_DIR / "input" / "3d", "*.glb")

# Copy 1.png to input/
copy_files(SCRIPT_DIR / "assets", COMFYUI_DIR / "input", "*.png")

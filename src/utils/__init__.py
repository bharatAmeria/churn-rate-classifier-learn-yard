import os
from pathlib import Path

def from_root(relative_path=""):
    """Get the absolute path from the project root."""
    return os.path.join(Path(__file__).resolve().parents[2], relative_path)

"""File utility functions for D2L Assignment Assistant."""

import os
import platform
import subprocess
from typing import Optional


def open_file_with_default_app(file_path: str) -> None:
    """
    Open file or folder with system default application (cross-platform).
    
    Args:
        file_path: Path to file or folder to open
    
    Raises:
        FileNotFoundError: If file/folder doesn't exist
        Exception: If platform is not supported or opening fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File or folder not found: {file_path}")
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # os.startfile works for both files and folders on Windows
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux and others
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        raise Exception(f"Could not open file or folder: {str(e)}")

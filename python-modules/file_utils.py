"""File utility functions for D2L Assignment Assistant."""

import os
import platform
import subprocess
import time
from typing import Optional

# Windows-specific imports for window management
if platform.system() == "Windows":
    try:
        import ctypes
        import ctypes.wintypes
        WINDOWS_API_AVAILABLE = True
    except ImportError:
        WINDOWS_API_AVAILABLE = False
else:
    WINDOWS_API_AVAILABLE = False


def arrange_windows_side_by_side(window_titles: list, delay: float = 1.0) -> bool:
    """
    Arrange windows side-by-side on Windows.
    
    Args:
        window_titles: List of partial window titles to find and arrange
        delay: Seconds to wait for windows to open before arranging
    
    Returns:
        True if successful, False otherwise
    """
    if not WINDOWS_API_AVAILABLE or platform.system() != "Windows":
        return False
    
    try:
        # Wait for windows to fully open
        time.sleep(delay)
        
        # Windows API functions
        user32 = ctypes.windll.user32
        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = user32.GetWindowTextW
        GetWindowTextLength = user32.GetWindowTextLengthW
        IsWindowVisible = user32.IsWindowVisible
        SetWindowPos = user32.SetWindowPos
        
        # Get screen dimensions
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        # Find windows
        found_windows = []
        
        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                title = buff.value
                
                # Check if any of our target titles are in the window title
                for target_title in window_titles:
                    if target_title.lower() in title.lower():
                        found_windows.append((hwnd, title))
                        break
            return True
        
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        
        # Arrange windows if we found both
        if len(found_windows) >= 2:
            # Calculate positions for side-by-side arrangement
            half_width = screen_width // 2
            
            # Left window (Excel/CSV)
            hwnd_left, title_left = found_windows[0]
            SetWindowPos(hwnd_left, 0, 0, 0, half_width, screen_height, 0x0040)  # SWP_SHOWWINDOW
            
            # Right window (PDF)
            hwnd_right, title_right = found_windows[1]
            SetWindowPos(hwnd_right, 0, half_width, 0, half_width, screen_height, 0x0040)
            
            return True
        
        return False
    except Exception:
        return False


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

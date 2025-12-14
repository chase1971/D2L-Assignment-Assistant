"""Backup utility functions for folder management."""

import os
import shutil
from typing import Callable, Optional


def backup_existing_folder(
    folder_path: str, 
    log_callback: Optional[Callable[[str], None]] = None,
    overwrite: bool = False
) -> bool:
    """
    If folder exists, either delete it (if overwrite=True) or rename it to a backup.
    Backup naming: "backup", "backup 2", "backup 3", etc. (no timestamps)
    
    Args:
        folder_path: Path to the folder to backup
        log_callback: Optional callback for logging messages
        overwrite: If True, delete the folder. If False, create a numbered backup.
    
    Returns:
        True if folder was handled (deleted or backed up), False if folder didn't exist
    """
    if not os.path.exists(folder_path):
        return False
    
    if overwrite:
        # Delete the folder
        if log_callback:
            log_callback("")
            log_callback("Existing folder found, deleting...")
            log_callback(f"   Deleting: {os.path.basename(folder_path)}")
        
        try:
            shutil.rmtree(folder_path)
            if log_callback:
                log_callback(f"   Folder deleted successfully")
                log_callback("")
            return True
        except Exception as e:
            if log_callback:
                log_callback(f"   Could not delete folder: {e}")
                log_callback("")
            return False
    else:
        # Create numbered backup
        parent_dir = os.path.dirname(folder_path)
        base_name = os.path.basename(folder_path)
        
        # Find the next available backup number
        backup_number = 1
        while True:
            if backup_number == 1:
                backup_name = f"{base_name} backup"
            else:
                backup_name = f"{base_name} backup {backup_number}"
            
            backup_path = os.path.join(parent_dir, backup_name)
            if not os.path.exists(backup_path):
                break
            backup_number += 1
        
        if log_callback:
            log_callback("")
            log_callback("Existing folder found, creating backup...")
            log_callback(f"   Renaming: {base_name}")
            log_callback(f"         to: {backup_name}")
        
        try:
            os.rename(folder_path, backup_path)
            if log_callback:
                log_callback(f"   Backup created successfully")
                log_callback("")
            return True
        except Exception as e:
            if log_callback:
                log_callback(f"   Could not create backup: {e}")
                log_callback("")
            return False

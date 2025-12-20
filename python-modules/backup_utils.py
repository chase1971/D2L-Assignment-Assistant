"""Backup utility functions for folder management."""

import os
import shutil
import time
from user_messages import log


def backup_existing_folder(
    folder_path: str, 
    overwrite: bool = False,
    suppress_logs: bool = False
) -> bool:
    """
    If folder exists, either delete it (if overwrite=True) or rename it to a backup.
    Backup naming: "backup", "backup 2", "backup 3", etc. (no timestamps)
    
    Args:
        folder_path: Path to the folder to backup
        overwrite: If True, delete the folder. If False, create a numbered backup.
    
    Returns:
        True if folder was handled (deleted or backed up), False if folder didn't exist
    """
    if not os.path.exists(folder_path):
        return False
    
    if overwrite:
        # Delete the folder
        log("EMPTY_LINE")
        log("BACKUP_DELETING_FOLDER")
        log("BACKUP_DELETING_NAME", name=os.path.basename(folder_path))
        
        try:
            shutil.rmtree(folder_path)
            log("BACKUP_DELETED")
            log("EMPTY_LINE")
            return True
        except Exception as e:
            log("BACKUP_DELETE_FAILED", error=str(e))
            log("EMPTY_LINE")
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
        
        if not suppress_logs:
            log("EMPTY_LINE")
            log("BACKUP_CREATING")
            log("BACKUP_RENAME_FROM", old_name=base_name)
            log("BACKUP_RENAME_TO", new_name=backup_name)
        
        try:
            os.rename(folder_path, backup_path)
            if not suppress_logs:
                log("BACKUP_SUCCESS")
                log("EMPTY_LINE")
            return True
        except (OSError, PermissionError) as e:
            # Check if it's a file locking issue (folder is open or file in use)
            if "Access is denied" in str(e) or "WinError 5" in str(e):
                log("BACKUP_FOLDER_IN_USE", folder_name=base_name)
            else:
                log("BACKUP_CREATE_FAILED", error=str(e))
            log("EMPTY_LINE")
            return False
        except Exception as e:
            log("BACKUP_CREATE_FAILED", error=str(e))
            log("EMPTY_LINE")
            return False

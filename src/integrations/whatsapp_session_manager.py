#!/usr/bin/env python3
"""
WhatsApp Session Manager
Advanced session management for WhatsApp Web automation with backup/restore functionality
"""

import os
import shutil
import logging
import time
import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppSessionManager:
    """
    Comprehensive session management for WhatsApp Web with backup/restore capabilities
    Similar to Node.js WhatsApp client session management
    """
    
    def __init__(self, base_session_path: str = "./chrome-session"):
        self.base_session_path = Path(base_session_path)
        self.session_path = self.base_session_path / "chrome-profile"
        self.backup_path = self.base_session_path / "backups"
        self.metadata_file = self.backup_path / "session_metadata.json"
        
        # Session validation settings
        self.max_session_age_hours = 168  # 7 days
        self.max_backups_to_keep = 5
        
        # Ensure directories exist
        self._ensure_directories()
        
        logger.info(f"Session Manager initialized with session path: {self.session_path}")
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        try:
            self.session_path.mkdir(parents=True, exist_ok=True)
            self.backup_path.mkdir(parents=True, exist_ok=True)
            logger.info("Session directories created successfully")
        except Exception as e:
            logger.error(f"Error creating session directories: {e}")
            raise
    
    def validate_session(self) -> Dict[str, any]:
        """
        Validate the current session integrity and freshness
        
        Returns:
            dict: Validation results with details
        """
        validation_result = {
            'valid': False,
            'session_exists': False,
            'profile_exists': False,
            'session_files_present': False,
            'session_age_valid': False,
            'backup_available': False,
            'details': []
        }
        
        try:
            # Check if session path exists
            if self.session_path.exists():
                validation_result['session_exists'] = True
                validation_result['details'].append("Session directory exists")
                
                # Check for Chrome profile files
                chrome_files = [
                    'Default/Preferences',
                    'Default/Cookies',
                    'Default/Local Storage',
                    'Default/Session Storage'
                ]
                
                profile_files_exist = any(
                    (self.session_path / file).exists() for file in chrome_files
                )
                
                if profile_files_exist:
                    validation_result['profile_exists'] = True
                    validation_result['details'].append("Chrome profile files found")
                
                # Check for WhatsApp-specific session files
                whatsapp_indicators = [
                    'Default/Local Storage/leveldb',
                    'Default/IndexedDB',
                    'Default/Session Storage'
                ]
                
                whatsapp_files_exist = any(
                    (self.session_path / indicator).exists() for indicator in whatsapp_indicators
                )
                
                if whatsapp_files_exist:
                    validation_result['session_files_present'] = True
                    validation_result['details'].append("WhatsApp session files detected")
                
                # Check session age
                session_age = self._get_session_age()
                if session_age and session_age < self.max_session_age_hours:
                    validation_result['session_age_valid'] = True
                    validation_result['details'].append(f"Session age: {session_age:.1f} hours (valid)")
                else:
                    validation_result['details'].append(f"Session age: {session_age:.1f} hours (expired)")
            
            # Check if backup is available
            if self._has_valid_backup():
                validation_result['backup_available'] = True
                validation_result['details'].append("Valid backup available")
            
            # Overall validation
            validation_result['valid'] = (
                validation_result['session_exists'] and
                validation_result['profile_exists'] and
                validation_result['session_files_present'] and
                validation_result['session_age_valid']
            )
            
            logger.info(f"Session validation result: {'VALID' if validation_result['valid'] else 'INVALID'}")
            
        except Exception as e:
            logger.error(f"Error during session validation: {e}")
            validation_result['details'].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def create_backup(self, backup_name: str = None) -> bool:
        """
        Create a backup of the current session
        
        Args:
            backup_name (str): Optional backup name, defaults to timestamp
            
        Returns:
            bool: Success status
        """
        try:
            if not self.session_path.exists():
                logger.warning("No session to backup - session path does not exist")
                return False
            
            # Generate backup name
            if backup_name is None:
                backup_name = f"session_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_dir = self.backup_path / backup_name
            
            logger.info(f"Creating session backup: {backup_name}")
            
            # Copy session directory to backup
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            
            shutil.copytree(self.session_path, backup_dir)
            
            # Update metadata
            self._update_backup_metadata(backup_name)
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            logger.info(f"Session backup created successfully: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating session backup: {e}")
            return False
    
    def restore_from_backup(self, backup_name: str = None) -> bool:
        """
        Restore session from backup
        
        Args:
            backup_name (str): Backup name to restore from, defaults to latest
            
        Returns:
            bool: Success status
        """
        try:
            # Find backup to restore
            if backup_name is None:
                backup_name = self._get_latest_backup()
            
            if backup_name is None:
                logger.error("No backups available to restore from")
                return False
            
            backup_dir = self.backup_path / backup_name
            
            if not backup_dir.exists():
                logger.error(f"Backup directory does not exist: {backup_dir}")
                return False
            
            logger.info(f"Restoring session from backup: {backup_name}")
            
            # Remove current session if it exists
            if self.session_path.exists():
                shutil.rmtree(self.session_path)
            
            # Copy backup to session directory
            shutil.copytree(backup_dir, self.session_path)
            
            logger.info(f"Session restored successfully from backup: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring session from backup: {e}")
            return False
    
    def ensure_session(self) -> Tuple[bool, str]:
        """
        Ensure a valid session exists, restore from backup if needed
        
        Returns:
            tuple: (success, status_message)
        """
        try:
            # First, validate current session
            validation = self.validate_session()
            
            if validation['valid']:
                return True, "Current session is valid"
            
            # If current session is invalid but backup exists, try restore
            if validation['backup_available']:
                logger.info("Current session invalid, attempting restore from backup...")
                if self.restore_from_backup():
                    return True, "Session restored from backup successfully"
                else:
                    return False, "Failed to restore session from backup"
            
            # No valid session or backup available
            return False, "No valid session or backup available - QR scan required"
            
        except Exception as e:
            logger.error(f"Error ensuring session: {e}")
            return False, f"Session management error: {str(e)}"
    
    def _get_session_age(self) -> Optional[float]:
        """Get session age in hours"""
        try:
            if not self.session_path.exists():
                return None
            
            # Get modification time of session directory
            session_mtime = os.path.getmtime(self.session_path)
            current_time = time.time()
            age_hours = (current_time - session_mtime) / 3600
            
            return age_hours
            
        except Exception as e:
            logger.error(f"Error getting session age: {e}")
            return None
    
    def _has_valid_backup(self) -> bool:
        """Check if valid backup exists"""
        try:
            if not self.backup_path.exists():
                return False
            
            # Look for backup directories
            backup_dirs = [d for d in self.backup_path.iterdir() if d.is_dir()]
            
            return len(backup_dirs) > 0
            
        except Exception as e:
            logger.error(f"Error checking for valid backup: {e}")
            return False
    
    def _get_latest_backup(self) -> Optional[str]:
        """Get the name of the most recent backup"""
        try:
            if not self.backup_path.exists():
                return None
            
            backup_dirs = [d for d in self.backup_path.iterdir() if d.is_dir()]
            
            if not backup_dirs:
                return None
            
            # Sort by modification time, newest first
            backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return backup_dirs[0].name
            
        except Exception as e:
            logger.error(f"Error getting latest backup: {e}")
            return None
    
    def _update_backup_metadata(self, backup_name: str):
        """Update backup metadata file"""
        try:
            metadata = {}
            
            # Load existing metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            # Add new backup info
            metadata[backup_name] = {
                'created': datetime.now().isoformat(),
                'session_path': str(self.session_path),
                'backup_path': str(self.backup_path / backup_name)
            }
            
            # Save metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating backup metadata: {e}")
    
    def _cleanup_old_backups(self):
        """Remove old backups to maintain storage limits"""
        try:
            if not self.backup_path.exists():
                return
            
            backup_dirs = [d for d in self.backup_path.iterdir() if d.is_dir()]
            
            if len(backup_dirs) <= self.max_backups_to_keep:
                return
            
            # Sort by modification time, oldest first
            backup_dirs.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove oldest backups
            backups_to_remove = backup_dirs[:-self.max_backups_to_keep]
            
            for backup_dir in backups_to_remove:
                logger.info(f"Removing old backup: {backup_dir.name}")
                shutil.rmtree(backup_dir)
                
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    def get_backup_info(self) -> List[Dict]:
        """Get information about available backups"""
        backup_info = []
        
        try:
            if not self.backup_path.exists():
                return backup_info
            
            backup_dirs = [d for d in self.backup_path.iterdir() if d.is_dir()]
            
            for backup_dir in backup_dirs:
                stat = backup_dir.stat()
                backup_info.append({
                    'name': backup_dir.name,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size_mb': sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file()) / (1024 * 1024)
                })
            
            # Sort by creation time, newest first
            backup_info.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting backup info: {e}")
        
        return backup_info
    
    def clear_session(self):
        """Clear current session (for fresh start)"""
        try:
            if self.session_path.exists():
                logger.info("Clearing current session...")
                shutil.rmtree(self.session_path)
                self._ensure_directories()
                logger.info("Session cleared successfully")
            else:
                logger.info("No session to clear")
                
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
    
    def get_session_status(self) -> Dict:
        """Get comprehensive session status"""
        validation = self.validate_session()
        backup_info = self.get_backup_info()
        
        return {
            'session_validation': validation,
            'session_path': str(self.session_path),
            'backup_path': str(self.backup_path),
            'available_backups': len(backup_info),
            'backup_details': backup_info[:3],  # Show only recent 3
            'session_age_hours': self._get_session_age()
        } 
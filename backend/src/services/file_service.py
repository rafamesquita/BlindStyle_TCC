"""
File management service for handling temporary files and directories.

This service provides utilities for creating and managing temporary files
with automatic cleanup using context managers.
"""

import tempfile
import shutil
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class FileService:
    """Service for managing temporary file operations."""
    
    @staticmethod
    @contextmanager
    def create_temp_image_file(image_data: bytes, suffix: str = ".jpg"):
        """
        Create a temporary image file from binary data with automatic cleanup.
        
        This context manager creates a temporary directory and file, writes the
        image data to it, and ensures cleanup happens automatically when exiting
        the context.
        
        Args:
            image_data: Binary image data to write to file
            suffix: File extension (default: ".jpg")
        
        Yields:
            Path: Path object pointing to the temporary image file
        
        Example:
            >>> image_bytes = base64.b64decode(base64_string)
            >>> with FileService.create_temp_image_file(image_bytes) as image_path:
            ...     # Use image_path here
            ...     process_image(image_path)
            ... # File and directory are automatically cleaned up here
        
        Raises:
            IOError: If file write operation fails
        """
        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            temp_path = Path(temp_dir)
            image_path = temp_path / f"temp_image{suffix}"
            
            # Write image data directly to file
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            logger.debug(f"Created temporary image file: {image_path}")
            
            # Yield the file path for use in the context
            yield image_path
            
        except Exception as e:
            logger.error(f"Error creating temporary file: {str(e)}")
            raise
            
        finally:
            # Cleanup: Remove temporary directory and all contents
            if temp_dir:
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory {temp_dir}: {str(e)}")
    
    @staticmethod
    def save_bytes_to_file(file_path: Path, data: bytes) -> None:
        """
        Save binary data to a file.
        
        Args:
            file_path: Destination file path
            data: Binary data to write
        
        Raises:
            IOError: If write operation fails
        """
        try:
            with open(file_path, 'wb') as f:
                f.write(data)
            logger.debug(f"Saved {len(data)} bytes to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file {file_path}: {str(e)}")
            raise

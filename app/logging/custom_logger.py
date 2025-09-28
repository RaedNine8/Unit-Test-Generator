import logging
import sys
from typing import Optional


class CustomLogger:
    """Custom logger class with simplified interface for the cover agent."""
    
    @staticmethod
    def get_logger(name: str, log_file: Optional[str] = None, level: str = "INFO", generate_log_files: bool = True) -> logging.Logger:
        """
        Get a configured logger instance.
        
        Args:
            name: Logger name
            log_file: Optional log file path
            level: Logging level
            generate_log_files: Whether to generate log files
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
            
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (only if generate_log_files is True)
        if generate_log_files and log_file:
            try:
                file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not create log file {log_file}: {e}")
        
        return logger

import logging
import sys

class CustomLogger:
    @staticmethod
    def get_logger(name: str, log_file: str = None, level: str = "INFO"):
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if not logger.handlers:
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            if log_file:
                fh = logging.FileHandler(log_file)
                fh.setFormatter(formatter)
                logger.addHandler(fh)
        return logger

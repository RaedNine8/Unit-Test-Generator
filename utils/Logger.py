import logging
import os


class Logger:
    @classmethod
    def get_logger(cls, name):
       
        logger = logging.getLogger(name)
        logger.setLevel(
            logging.DEBUG
        )  # Set the logger to handle all messages of DEBUG level and above

        # Specify the log file path
        log_file_path = "run.log"

      

        return logger

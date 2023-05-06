import os
import logging


class Tools:
    def __init__(self):
        """
            Instantiate an object for the Tools class
        """
        pass

    @staticmethod
    def get_logger(log_path):
        """
            Create a Logging object
        """
        try:
            logger = logging.getLogger(str(log_path).split("/")[-1])
            if not logger.hasHandlers():
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

                file_handler = logging.FileHandler(os.path.join(log_path, 'output.log'), mode='w+')
                file_handler.setFormatter(formatter)

                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(formatter)

                logger.setLevel(logging.INFO)
                logger.addHandler(file_handler)
                logger.addHandler(stream_handler)

            return logger
        except Exception as ve:
            print(ve)
            raise
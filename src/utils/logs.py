import logging
import os
import sys
from datetime import datetime


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-6s] %(message)s",  # Left-align the levelname to 6 chars
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    p = os.path.dirname
    log_dir = os.path.join(p(p(p(os.path.abspath(__file__)))), "logs", f"app_{timestamp}")
    print(log_dir)
    os.makedirs(log_dir, exist_ok=True)  # create directory if not exists

    log_file = os.path.join(log_dir, "app.log")

    file_handler = logging.FileHandler(log_file, mode='a')  # 'a' = append
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

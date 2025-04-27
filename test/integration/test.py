from src.utils.logs import setup_logging
import logging

if __name__ == "__main__":
    setup_logging()
    logging.info("Voila info")
    logging.error("Voila error")

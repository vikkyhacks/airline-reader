from airlines_reader.utils.logging_config import setup_logging
import logging

if __name__ == "__main__":
    setup_logging()
    logging.info("Voila info")
    logging.error("Voila error")

import logging
from common.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def saveResulte():
    with open('files/Step2.json', 'r') as f:
        logger.info("Read Step2.py")
        txt = f.readlines()
        logger.info(txt)


def main():
    logger.info("Starting main")
    saveResulte()
    logger.info("End main")


if __name__=='__main__':
    main()
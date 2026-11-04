import logging
from common.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def saveResulte():
    with open('files/Step1.json', 'w') as f:
        logger.info("Writing Step1.py")
        f.write('test 1')



def main():
    logger.info("Starting main")
    saveResulte()
    logger.info("End main")


if __name__=='__main__':
    main()
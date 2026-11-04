import logging
from common.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def saveResulte():
    with open('Step1.json', 'r') as f:
        logger.info("Read Step1.py")
        txt = f.readlines()
        logger.info(txt)
    
    with open('Step2.json', 'w') as f:
        logger.info("Writing Step2.py")
        f.write('test 2')



def main():
    logger.info("Starting main")
    saveResulte()
    logger.info("End main")


if __name__=='__main__':
    main()
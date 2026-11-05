import logger as log

log.setup_logging()
logger = log.get_logger(__name__)


def saveResulte():
    with open('Step1.json', 'w') as f:
        logger.info("Writing Step1.py")
        f.write('test 1')



def main():
    logger.info("Starting main")
    saveResulte()
    logger.info("End main")


if __name__=='__main__':
    main()
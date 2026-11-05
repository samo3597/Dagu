import logger as log
import GoogleAI

log.setup_logging()
logger = log.get_logger(__name__)


def saveResulte():
    with open('Step1.json', 'r') as f:
        logger.info("Read Step1.py")
        txt = f.readlines()
        logger.info(txt)

    logger.info("Starting process_product_batch")
    Res = GoogleAI.process_product_batch(txt)
    logger.info("End process_product_batch")
    
    with open('Step2.json', 'w') as f:
        logger.info("Writing Step2.py")
        f.write('test 2')



def main():
    logger.info("Starting main")
    saveResulte()
    logger.info("End main")


if __name__=='__main__':
    main()
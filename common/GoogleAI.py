import logger as log

log.setup_logging()
logger = log.getLogger(__name__)

def process_product_batch(data):
    logger.info("start process_product_batch")

    return True
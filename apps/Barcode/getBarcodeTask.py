import variables as var
import logger as log
import requests
import json

log.setup_logging()
logger = log.get_logger(__name__)

API_URL = var.get_env("API_URL")


def saveResulte():

    try:
        logger.info(f"Fetching data from API")
        response = requests.get(API_URL)
        response.raise_for_status()

        logger.info(f"Response received: {response.status_code}")
        json_data = response.json()
    
        with open("files/Step1.json", "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)

        logger.info(f"Success! JSON data successfully saved to Step1.json")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network or HTTP Error occurred: {e}")
    except json.JSONDecodeError:
        logger.error("❌ Failed to parse response as JSON.")
    except IOError:
        logger.error("❌ File write error occurred.")



def main():
    logger.info("Starting main")
    saveResulte()
    logger.info("End main")


if __name__=='__main__':
    main()
import json
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from Constant import Constant

PATH_ERROR = " does not exist. Exiting the app."


def validate_paths():
    """This Method Validates the important file paths
       This method is a fail safe during movement of the file during
       infustructure change
    """
    if not os.path.exists(Constant.DATA_DIR):
        print("Deploy Directory " + Constant.DATA_DIR +
              PATH_ERROR)
        sys.exit(1)

    if not os.path.exists(Constant.LOG_DIR):
        print("Logfile Directory " + Constant.LOG_DIR +
              PATH_ERROR)
        sys.exit(1)

    if not os.path.exists(Constant.CONFIG_DIR):
        print("Logfile Directory " + Constant.CONFIG_DIR +
              PATH_ERROR)
        sys.exit(1)


def read_config():
    filepath = Constant.CONFIG_DIR + '/config.json'
    with open(filepath, 'r') as file:
        config_data = json.load(file)
    # logging.info(config_data)
    return config_data


def is_holiday(holiday_list):
    logging.info('Checking for Trade Holiday')
    today = datetime.today().strftime('%d/%m/%Y')
    if today in holiday_list:
        logging.info('Today Is Trade Holiday')
        notify_message('Today is Trading Holiday', Constant.MESSAGE_INFO)
        sys.exit(0)


def initialize_log(file_name):
    """This Method Initialize the Logfile

    Args:
        file_name (str): Absolute Path of the Logfile
    """

    logger = logging.getLogger()
    handler = TimedRotatingFileHandler(
        file_name, when='midnight', backupCount=5)
    formatter = logging.Formatter("%(asctime)s||%(levelname)s||"
                                  "%(filename)s||%(funcName)s"
                                  "||%(lineno)d||%(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info('Starting The Application')
    logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++")


def generate_session():
    validate_paths()
    initialize_log(Constant.LOG_DIR + "/Login.log")
    config_data = read_config()
    is_holiday(config_data['trade_holidays'])


def app():
    generate_session()


app()

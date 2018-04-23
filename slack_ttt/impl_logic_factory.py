import logging
from .logger import log_entry_exit, setup_logging
from settings import TTT_LOGIC_SOURCE
from .native import NativeLogicSource
from .salesforce import SalesforceLogicSource

setup_logging()
logger = logging.getLogger(__name__)

class ImplLogicFactory(object):

    @staticmethod
    def get_logic_source():
        if TTT_LOGIC_SOURCE == 'salesforce':
            return SalesforceLogicSource()
        else:
            return NativeLogicSource()



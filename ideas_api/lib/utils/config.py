#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Copyright 2024, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the California Institute of
#  Technology.  This software is subject to U.S. export control laws and regulations
#  and has been classified as EAR99.  By accepting this software, the user agrees to
#  comply with all applicable U.S. export laws and regulations.  User has the
#  responsibility to obtain export licenses, or other export authority as may be
#  required before exporting such information to foreign countries or providing
#  access to foreign persons.
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os

from dotenv import load_dotenv

from ideas_api.lib.utils.singleton_base import Singleton


class Config(metaclass=Singleton):
    ES_URL = 'ES_URL'
    ES_PORT = 'ES_PORT'
    SNS_TOPIC = 'SNS_TOPIC'
    ADMIN_GROUPS = 'ADMIN_GROUPS'
    CACHING_JOBS = 'CACHING_JOBS'
    DEFAULT_CONFIG_JOBS = '100'
    def __init__(self):
        load_dotenv()
        self.__mandatory_keys = [
            Config.ES_URL,
            Config.SNS_TOPIC,
        ]
        self.__validate()

    def __validate(self):
        missing_mandatory_keys = [k for k in self.__mandatory_keys if k not in os.environ]
        if len(missing_mandatory_keys) > 0:
            raise RuntimeError('missing configuration values in environment values: {}'.format(missing_mandatory_keys))
        return

    def get_value(self, key, default_val=None):
        if key in os.environ:
            return os.environ[key]
        return default_val

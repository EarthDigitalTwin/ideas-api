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

import logging
import os
from copy import deepcopy

import boto3
from ideas_api.lib.aws_base.aws_constants import AwsConstants

LOGGER = logging.getLogger(__name__)


class AwsCred:
    def __init__(self):
        self.__region = os.getenv(AwsConstants.aws_region, AwsConstants.default_region)
        LOGGER.debug(f'using region: {self.__region}')
        self.__boto3_session = {'region_name': self.__region}
        aws_access_key_id = os.getenv(AwsConstants.aws_access_key_id, '')
        aws_secret_access_key = os.getenv(AwsConstants.aws_secret_access_key, '')
        aws_session_token = os.getenv(AwsConstants.aws_session_token, '')
        if aws_access_key_id != '':
            LOGGER.debug('using aws_access_key_id as it is not empty')
            if aws_secret_access_key == '':
                raise ValueError(f'missing aws_secret_access_key for aws_access_key_id ends with {aws_access_key_id[-3:]}')
            self.__boto3_session['aws_access_key_id'] = aws_access_key_id
            self.__boto3_session['aws_secret_access_key'] = aws_secret_access_key
            if aws_session_token != '':
                LOGGER.debug('adding aws_session_token as it is not empty and aws_access_key_id exists')
                self.__boto3_session['aws_session_token'] = aws_session_token
        else:
            LOGGER.debug('using default session as there is  no aws_access_key_id')

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, val):
        """
        :param val:
        :return: None
        """
        self.__region = val
        return

    @property
    def boto3_session(self):
        return self.__boto3_session

    @boto3_session.setter
    def boto3_session(self, val):
        """
        :param val:
        :return: None
        """
        self.__boto3_session = val
        return

    def get_session(self):
        return boto3.Session(**self.boto3_session)

    def get_resource(self, service_name: str):
        return boto3.Session(**self.boto3_session).resource(service_name)

    def get_client(self, service_name: str, **kwargs):
        new_args = deepcopy(kwargs)
        new_args['service_name'] = service_name
        return boto3.Session(**self.boto3_session).client(**new_args)

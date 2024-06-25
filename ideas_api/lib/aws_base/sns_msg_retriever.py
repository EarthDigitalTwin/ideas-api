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

import json
import logging

from ideas_api.lib.utils.parallel_json_validator import SingleJsonValidator
LOGGER = logging.getLogger(__name__)


class LambdaEventMsgRetriever:
    SQS_MSG_SCHEMA = {
        'type': 'object',
        'properties': {
            'Records': {
                'type': 'array',
                'minItems': 1,
                'maxItems': 1,  # TODO only accept 1 item?
                'items': {
                    'type': 'object',
                    'properties': {
                        'body': {'type': 'string', 'minLength': 1}
                    },
                    'required': ['body']
                }
            }
        },
        'required': ['Records']
    }

    SNS_MSG_SCHEMA = {
        "type": "object",
        "properties": {
            "Type": {"type": "string"},
            "MessageId": {"type": "string"},
            "TopicArn": {"type": "string"},
            "Subject": {"type": "string"},
            "Timestamp": {"type": "string"},
            "SignatureVersion": {"type": "string"},
            "Signature": {"type": "string"},
            "SigningCertURL": {"type": "string"},
            "UnsubscribeURL": {"type": "string"},
            "Message": {"type": "string"},
        },
        "required": ["Message"]
    }

    def __init__(self):
        self.a = 1

    def from_sqs(self, sqs_msg):
        result, errors = SingleJsonValidator().load_schema(self.SQS_MSG_SCHEMA).validate(sqs_msg)
        if result is False:
            raise ValueError(f'sqs_msg did not pass SQS_MSG_SCHEMA: {errors}')

        # TODO validate sqs
        sns_msgs = []
        for each_msg in sqs_msg['Records']:
            sns_msg = json.loads(each_msg['body'])
            result, errors = SingleJsonValidator().load_schema(self.SNS_MSG_SCHEMA).validate(sns_msg)
            if result is False:
                LOGGER.error(f'sns_msg did not pass SNS_MSG_SCHEMA: {errors}. msg: {sns_msg}')
                continue
            sns_msgs.append(json.loads(sns_msg['Message']))
        return sns_msgs

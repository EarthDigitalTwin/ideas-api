"""
{
  "Records": [
    {
      "messageId": "6210f778-d081-4ae9-a861-8534d612dfae",
      "receiptHandle": "<encoded id>",
      "body": "<JSON String. See Below>",
      "attributes": {
        "ApproximateReceiveCount": "6",
        "SentTimestamp": "1644255065441",
        "SenderId": "<ID>",
        "ApproximateFirstReceiveTimestamp": "1644255065441"
      },
      "messageAttributes": {},
      "md5OfBody": "<MD5>",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws-us-gov:sqs:<REGION>:<ACCOUNT-ID>:send_records_to_es",
      "awsRegion": "us-gov-west-1"
    }
  ]
}
#######
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-gov-west-1",
      "eventTime": "2022-02-07T17:31:04.498Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "AWS:ID:USER"
      },
      "requestParameters": {
        "sourceIPAddress": "128.149.246.219"
      },
      "responseElements": {
        "x-amz-request-id": "ID",
        "x-amz-id-2": "ID"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "all-obj-create",
        "bucket": {
          "name": "lsmd-data-bucket",
          "ownerIdentity": {
            "principalId": "440216117821"
          },
          "arn": "arn:aws-us-gov:s3:::lsmd-data-bucket"
        },
        "object": {
          "key": "manual_test/zipped_upload/jpl.calendar.2022.png",
          "size": 841141,
          "eTag": "tag",
          "sequencer": "ID"
        }
      }
    }
  ]
}
"""
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
from urllib.parse import unquote_plus

from ideas_api.lib.utils.parallel_json_validator import SingleJsonValidator

# from lsmd_lambda_functions.s3_records.s3_event_validator_abstract import S3EventValidatorAbstract
# from lsmd_lambda_functions.utils.general_utils import GeneralUtils
# from lsmd_lambda_functions.utils.lambda_logger_generator import LambdaLoggerGenerator

LOGGER = logging.getLogger(__name__)


class SqsMsgTransformer:
    OUTER_SCHEMA = {
        'type': 'object',
        'properties': {
            'Records': {
                'type': 'array',
                'minItems': 1,
                'maxItems': 1,
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
    S3_RECORD_SCHEMA = {
        'type': 'object',
        'properties': {'Records': {
            'type': 'array',
            'minItems': 1,
            'maxItems': 1,
            'items': {
                'type': 'object',
                'properties': {'s3': {
                    'type': 'object',
                    'properties': {
                        'bucket': {
                            'type': 'object',
                            'properties': {'name': {'type': 'string', 'minLength': 1}},
                            'required': ['name']
                        },
                        'object': {
                            'type': 'object',
                            'properties': {'key': {'type': 'string', 'minLength': 1}},
                            'required': ['key']
                        }},
                    'required': ['bucket', 'object']
                }},
                'required': ['s3']
            }
        }},
        'required': ['Records']
    }

    def get_sns_msg(self, event):
        validation_result, validation_details = SingleJsonValidator().load_schema(self.OUTER_SCHEMA).validate(event)
        if not validation_result:
            raise ValueError(f'invalid sqs msg: {validation_details}')
        sns_msg = event['Records'][0]['body']
        # TODO confirm that body is already SNS msg.
        return sns_msg

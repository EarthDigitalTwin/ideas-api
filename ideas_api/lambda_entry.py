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
import os

from ideas_api.lib.aws_base.aws_lambda import AwsLambda
from ideas_api.lib.job_management.job_constants import JobConstants

def trigger_job_updater(event, context):
    """
    :param event:
    :param context:
    :return:
    """
    endpoint_path = f'{JobConstants.JOB_API_PREFIX}{JobConstants.JOB_API_ENDPOINT}'
    update_message_body = {}
    update_job_payload = {
        "resource": endpoint_path,
        "path": endpoint_path,
        "httpMethod": "POST",
        "headers": None,
        "multiValueHeaders": None,
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "kl8oru",
            "resourcePath": endpoint_path,
            "httpMethod": "GET",
            "extendedRequestId": "AVbmYGmaPHcFhVQ=",
            "requestTime": "14/Feb/2023:15:18:00 +0000",
            "path": endpoint_path,
            "accountId": "237868187491",
            "protocol": "HTTP/1.1",
            "stage": "test-invoke-stage",
            "domainPrefix": "testPrefix",
            "requestTimeEpoch": 1676387880557,
            "requestId": "729d6e14-27e9-4c84-b9f3-b6f9b3e10ae0",
            "identity": {},
            "domainName": "testPrefix.testDomainName",
            "apiId": "1gp9st60gd"
        },
        "body": json.dumps(update_message_body),
        "isBase64Encoded": False
    }
    job_management_lambda_name = os.environ.get('COLLECTION_CREATION_LAMBDA_NAME').strip()
    response = AwsLambda().invoke_function(
        function_name=job_management_lambda_name,
        payload=update_job_payload,
    )
    return {
        'statusCode': 202,
        'body': json.dumps({
            'message': 'processing'
        })
    }

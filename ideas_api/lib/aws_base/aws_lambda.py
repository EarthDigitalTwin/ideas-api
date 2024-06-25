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

from ideas_api.lib.aws_base.aws_cred import AwsCred


class AwsLambda(AwsCred):
    def __init__(self):
        super().__init__()
        self.__lambda_client = self.get_client('lambda')

    def invoke_function(self, function_name: str, payload: dict):
        response = self.__lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',  # 'Event' = async | 'RequestResponse' = sync | 'DryRun',
            LogType='None',  # 'None' = async | 'Tail =  sync',
            ClientContext='',  # Up to 3583 bytes of base64-encoded data
            Payload=json.dumps(payload).encode(),
            # Qualifier='string'
        )
        return response

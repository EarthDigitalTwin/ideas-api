import base64
import json
import logging

from fastapi import APIRouter, HTTPException, Request, Response

LOGGER = logging.getLogger(__name__)
# LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())


class FastApiUtils:
    @staticmethod
    def get_authorization_info(request: Request):
        """
        :return:
        """
        action = request.method
        resource = request.url.path
        bearer_token = request.headers.get('Authorization', '')
        LOGGER.debug(f'raw bearer_token: {bearer_token}')
        username_part = bearer_token.split('.')[1]
        jwt_decoded = base64.standard_b64decode(f'{username_part}========'.encode()).decode()
        LOGGER.debug(f'jwt_decoded: {jwt_decoded}')
        jwt_decoded = json.loads(jwt_decoded)
        ldap_groups = jwt_decoded['cognito:groups']
        username = jwt_decoded['cognito:username']
        return {
            'username': username,
            'ldap_groups': list(set(ldap_groups)),
            'action': action,
            'resource': resource,
        }

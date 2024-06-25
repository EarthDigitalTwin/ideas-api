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

from elasticsearch import Elasticsearch, RequestsHttpConnection
from ideas_api.lib.aws_base.aws_cred import AwsCred
from ideas_api.lib.external_io.es_middleware import ESMiddleware
from requests_aws4auth import AWS4Auth

LOGGER = logging.getLogger(__name__)


class EsMiddlewareAws(ESMiddleware):

    def __init__(self, index, base_url, port=443) -> None:
        super().__init__(index, base_url, port)
        base_url = base_url.replace('https://', '')  # hide https
        self._index = index
        aws_cred = AwsCred()
        service = 'es'
        credentials = aws_cred.get_session().get_credentials()
        aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, aws_cred.region, service,
                            session_token=credentials.token)
        self._engine = Elasticsearch(
            hosts=[{'host': base_url, 'port': port}],
            http_auth=aws_auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

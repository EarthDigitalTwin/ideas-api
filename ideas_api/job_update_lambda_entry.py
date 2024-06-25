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

from ideas_api.lib.aws_base.sns_msg_retriever import LambdaEventMsgRetriever
from ideas_api.lib.external_io.es_abstract import ESAbstract
from ideas_api.lib.external_io.es_factory import ESFactory
from ideas_api.lib.external_io.pub_sub_abstract import PubSubAbstract
from ideas_api.lib.external_io.pub_sub_factory import PubSubFactory
from ideas_api.lib.processes.ogc_job_updater import OgcJobUpdater
from ideas_api.lib.utils.config import Config


def trigger_job_updater(event, context):
    """ES_URL=https://search-ideas-api-dev-1-f62xltsguioft2hpjepkrhln3e.us-west-2.es.amazonaws.com
ES_PORT=443
SNS_TOPIC=arn:aws:sns:<REGION>:<ACCOUNT-ID>:ideas-project-ideas_api_main_topic
aws_region=us-west-2"""
    print(event)
    config = Config()
    es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                         base_url=config.get_value(Config.ES_URL),
                                                         port=int(config.get_value(Config.ES_PORT, '443')),
                                                         index='NA')

    pub_sub: PubSubAbstract = PubSubFactory().get_instance('SNS').set_channel(config.get_value(Config.SNS_TOPIC))
    job_updater = OgcJobUpdater(es_middleware, pub_sub)
    real_msgs = LambdaEventMsgRetriever().from_sqs(event)
    for each_real_msg in real_msgs:
        job_updater.process_update(each_real_msg)
    return

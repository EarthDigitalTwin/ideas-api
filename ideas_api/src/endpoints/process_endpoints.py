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

from fastapi import APIRouter, HTTPException, Request
from ideas_api.lib.external_io.es_abstract import ESAbstract
from ideas_api.lib.external_io.es_factory import ESFactory
from ideas_api.lib.external_io.pub_sub_abstract import PubSubAbstract
from ideas_api.lib.external_io.pub_sub_factory import PubSubFactory
from ideas_api.lib.job_management.job_constants import JobConstants
from ideas_api.lib.processes.ogc_processes import OgcProcess
from ideas_api.lib.utils.config import Config
from ideas_api.lib.utils.fast_api_utils import FastApiUtils
from ideas_api.src.in_out_models.in_out_models import NewJobItem, JobStatusResponse, ProcessPayload, ProcessOverviewResponse

LOGGER = logging.getLogger(__name__)

router = APIRouter(
    prefix=f'/{JobConstants.PROCESSES}',
    tags=["Process CRUD"],
    responses={404: {"description": "Not found"}},
)
"""
TODO

- stage names to start with job id  # NA
- ancillaryProcessResults -> intermediate/ staged results  # Done. But this is data level. 
- log aggregation (link to log aggregator in DB for details)  # Done. there is a logging table to store all logs & updates for eahc job id. 
- job reminders for manual jobs  # TODO
- status to be uppercase  # Done. all are uppercase
- Ohio basin in the list  # TODO. This is at data level. Kevin to provide it. 
- processes to check for cached result (previous result)  # Delegated. applications will return it as they know better which cached results matches the time ranges from job id 
"""
@router.put("")
async def create_new_process(request: Request, new_job_item: ProcessPayload):
    """

    Example Test Case: https://github.jpl.nasa.gov/IDEAS/ideas-api/blob/ogc.proposal/tests/integration_tests/test_ogc_processes.py#L37

    Example Process Payload: https://github.jpl.nasa.gov/IDEAS/ideas-api/blob/ogc.proposal/ogc.proposal/ogc.process.storage.json

    Example Process Payload Schema: https://github.jpl.nasa.gov/IDEAS/ideas-api/blob/ogc.proposal/ogc.proposal/ogc.processes.schema.dict.json

    ---
    """
    config = Config()
    auth_info = FastApiUtils.get_authorization_info(request)
    defined_admin_groups = json.loads(config.get_value(Config.ADMIN_GROUPS, '[]'))
    token_user_groups = set(auth_info['ldap_groups'])
    LOGGER.debug(f'defined_admin_groups v. token_user_groups: {defined_admin_groups} v. {token_user_groups}')
    is_admin = [k for k in defined_admin_groups if k in token_user_groups]
    is_admin = len(is_admin) > 0
    LOGGER.debug(f'is_admin: {is_admin}')
    if not is_admin:
        raise HTTPException(status_code=403, detail=f'user is not admin. {defined_admin_groups}')

    es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                         base_url=config.get_value(Config.ES_URL),
                                                         port=int(config.get_value(Config.ES_PORT, '443')),
                                                         index='NA')
    try:
        OgcProcess(es_middleware, None).create_new_process(new_job_item.dict())
    except Exception as e:
        LOGGER.exception('failed during create_new_job')
        raise HTTPException(status_code=500, detail=str(e))
    return {'message': 'registered'}


@router.get("")
async def get_all_processes(request: Request) -> ProcessOverviewResponse:
    """

    Example Test Case: https://github.jpl.nasa.gov/IDEAS/ideas-api/blob/ogc.proposal/tests/integration_tests/test_ogc_processes.py#L281

    ---
    """
    config = Config()
    es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                         base_url=config.get_value(Config.ES_URL),
                                                         port=int(config.get_value(Config.ES_PORT, '443')),
                                                         index='NA')
    try:
        all_process_summaries = OgcProcess(es_middleware, None).get_all_processes()
    except Exception as e:
        LOGGER.exception('failed during get_all_processes')
        raise HTTPException(status_code=500, detail=str(e))
    return {'processes': all_process_summaries}


@router.get("/{process_id}")
async def get_single_process(request: Request, process_id: str, version_id: str = '') -> ProcessPayload:
    """

    Example Test Case: https://github.jpl.nasa.gov/IDEAS/ideas-api/blob/ogc.proposal/tests/integration_tests/test_ogc_processes.py#L293

    ---
    """
    config = Config()
    es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                         base_url=config.get_value(Config.ES_URL),
                                                         port=int(config.get_value(Config.ES_PORT, '443')),
                                                         index='NA')
    try:
        process_details = OgcProcess(es_middleware, None).get_single_process(process_id, version=version_id)
    except Exception as e:
        LOGGER.exception('failed during get_single_process')
        raise HTTPException(status_code=500, detail=str(e))
    return process_details


@router.post("/{process_id}/execution")
async def execute_new_job(request: Request, new_job: NewJobItem, process_id: str, version_id: str = '') -> JobStatusResponse:
    """

    Example Test Case: https://github.jpl.nasa.gov/IDEAS/ideas-api/blob/ogc.proposal/tests/integration_tests/test_ogc_processes.py#L306

    Example New Job Item: https://github.jpl.nasa.gov/IDEAS/ideas-api/blob/ogc.proposal/ogc.proposal/ogc.job.storage.example.json

    ---
    """
    config = Config()
    es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                         base_url=config.get_value(Config.ES_URL),
                                                         port=int(config.get_value(Config.ES_PORT, '443')),
                                                         index='NA')
    pub_sub: PubSubAbstract = PubSubFactory().get_instance('SNS').set_channel(config.get_value(Config.SNS_TOPIC))
    try:
        new_job_response = OgcProcess(es_middleware, pub_sub).create_new_instance(process_id, new_job.dict(), version_id)
    except Exception as e:
        LOGGER.exception('failed during execute_new_job')
        raise HTTPException(status_code=500, detail=str(e))
    return new_job_response

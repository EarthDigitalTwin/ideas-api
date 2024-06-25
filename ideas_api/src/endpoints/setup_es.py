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

from fastapi import APIRouter, HTTPException

from ideas_api.lib.external_io.es_abstract import ESAbstract
from ideas_api.lib.external_io.es_factory import ESFactory
from ideas_api.lib.job_management.job_constants import JobConstants, JOB_INDEX_MAPPING, OGC_PROCESS_MAPPING, \
    OGC_JOB_MAPPING, JOB_STAGE_LOGS_MAPPING
from ideas_api.lib.utils.config import Config

router = APIRouter(
    prefix="/setup_es",
    tags=["ES"],
    responses={404: {"description": "Not found"}},
)
LOGGER = logging.getLogger(__name__)


@router.put("")
async def setup_es():
    config = Config()
    es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                         base_url=config.get_value(Config.ES_URL),
                                                         port=int(config.get_value(Config.ES_PORT, '443')),
                                                         index='NA')
    index_name = f'{JobConstants.JOB_INDEX_ALIAS}_1'
    errors = []
    try:
        es_middleware.create_index(f'{JobConstants.OGC_PROCESS_INDEX_ALIAS}_1', OGC_PROCESS_MAPPING)
        es_middleware.create_alias(f'{JobConstants.OGC_PROCESS_INDEX_ALIAS}_1', JobConstants.OGC_PROCESS_INDEX_ALIAS)
    except Exception as e:
        LOGGER.exception(f'failed to create index / alias - {JobConstants.OGC_PROCESS_INDEX_ALIAS}: {str(e)}')
        errors.append(f'failed to create index / alias - {JobConstants.OGC_PROCESS_INDEX_ALIAS}: {str(e)}')
    try:
        es_middleware.create_index(f'{JobConstants.OGC_JOB_INDEX_ALIAS}_1', OGC_JOB_MAPPING)
        es_middleware.create_alias(f'{JobConstants.OGC_JOB_INDEX_ALIAS}_1', JobConstants.OGC_JOB_INDEX_ALIAS)
    except Exception as e:
        LOGGER.exception(f'failed to create index / alias - {JobConstants.OGC_PROCESS_INDEX_ALIAS}: {str(e)}')
        errors.append(f'failed to create index / alias - {JobConstants.OGC_PROCESS_INDEX_ALIAS}: {str(e)}')
    try:
        es_middleware.create_index(f'{JobConstants.OGC_JOB_LOGS_INDEX_ALIAS}_1', JOB_STAGE_LOGS_MAPPING)
        es_middleware.create_alias(f'{JobConstants.OGC_JOB_LOGS_INDEX_ALIAS}_1', JobConstants.OGC_JOB_LOGS_INDEX_ALIAS)
    except Exception as e:
        LOGGER.exception(f'failed to create index / alias - {JobConstants.OGC_PROCESS_INDEX_ALIAS}: {str(e)}')
        errors.append(f'failed to create index / alias - {JobConstants.OGC_PROCESS_INDEX_ALIAS}: {str(e)}')
    # es_middleware.create_index(index_name, JOB_INDEX_MAPPING)
    # es_middleware.create_alias(index_name, JobConstants.JOB_INDEX_ALIAS)
    if len(errors) > 0:
        raise HTTPException(status_code=500, detail=json.dumps(errors))
    return {'status': 'finished'}

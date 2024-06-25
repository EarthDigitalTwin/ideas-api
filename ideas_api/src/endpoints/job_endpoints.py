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

from fastapi import APIRouter, HTTPException, Request
from ideas_api.lib.external_io.es_abstract import ESAbstract
from ideas_api.lib.external_io.es_factory import ESFactory
from ideas_api.lib.job_management.job_constants import JobConstants
from ideas_api.lib.processes.ogc_jobs import OgcJobs
from ideas_api.lib.utils.config import Config
from ideas_api.src.in_out_models.in_out_models import JobStatusResponse, JobResultResponse

LOGGER = logging.getLogger(__name__)

router = APIRouter(
    prefix=f'/{JobConstants.JOBS}',
    tags=["JOBS CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{job_id}")
async def get_job_status(request: Request, job_id: str) -> JobStatusResponse:
    LOGGER.debug(f"Authorization: {request.headers['Authorization']}")
    config = Config()
    es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                         base_url=config.get_value(Config.ES_URL),
                                                         port=int(config.get_value(Config.ES_PORT, '443')),
                                                         index='NA')
    try:
        job_status = OgcJobs(es_middleware).get_job_status(job_id)
    except Exception as e:
        LOGGER.exception('failed during get_job_status')
        raise HTTPException(status_code=500, detail=str(e))
    return job_status


@router.get("/{job_id}/results")
async def get_job_result(request: Request, job_id: str) -> JobResultResponse:
    config = Config()
    es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                         base_url=config.get_value(Config.ES_URL),
                                                         port=int(config.get_value(Config.ES_PORT, '443')),
                                                         index='NA')
    try:
        job_result = OgcJobs(es_middleware).get_job_result(job_id)
    except Exception as e:
        LOGGER.exception('failed during get_job_status')
        raise HTTPException(status_code=500, detail=str(e))
    return job_result

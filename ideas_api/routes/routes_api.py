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

from fastapi import APIRouter

from ideas_api.src.endpoints import job_endpoints
from ideas_api.src.endpoints import process_endpoints
from ideas_api.src.endpoints import setup_es


main_router = APIRouter()
main_router.include_router(setup_es.router)
main_router.include_router(process_endpoints.router)
main_router.include_router(job_endpoints.router)

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
import os

import uvicorn
from fastapi import FastAPI
from mangum import Mangum
from starlette.requests import Request

from ideas_api.lib.job_management.job_constants import JobConstants
from ideas_api.routes.routes_api import main_router

if logging.getLogger().hasHandlers():
    # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
    # `.basicConfig` does not execute. Thus we set the level directly.
    logging.getLogger().setLevel(int(os.environ.get('LOG_LEVEL', '20')))
else:
    logging.basicConfig(level=int(os.environ.get('LOG_LEVEL', '20')), format="%(asctime)s [%(levelname)s] [%(name)s::%(lineno)d] %(message)s")

app = FastAPI(title='Ideas API',
              description='API using OGC Processes')
app.include_router(main_router, prefix=JobConstants.JOB_API_PREFIX)

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}


# to make it work with Amazon Lambda, we create a handler object
handler = Mangum(app=app)

if __name__ == '__main__':
    uvicorn.run("web_service:app", port=8005, log_level="info", reload=True)
    print("running")
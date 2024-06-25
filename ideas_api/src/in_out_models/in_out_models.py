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
from typing import Optional, Union

from pydantic import BaseModel


class SpatialCoverage(BaseModel):
    bbox: list[float]

class StagedResult(BaseModel):
    name: str
    value: str

class Inputs(BaseModel):
    executingStageFlags: list[bool]
    stagedResults: list[StagedResult]
    scenario: str
    hydroModel: str
    basinId: int
    precipitationType: str
    landSurfaceModel: str
    spatialResolution: str
    startTime: str
    endTime: str
    spatialCoverage: SpatialCoverage


class NewJobItem(BaseModel):
    inputs: dict


class ProcessOverviewSingle(BaseModel):
    id: str
    version: str
    title: str
    description: str


class ProcessOverviewResponse(BaseModel):
    processes: list[ProcessOverviewSingle]

class JobResultResponse(BaseModel):
    processResults: list[StagedResult]


class JobStatusResponse(BaseModel):
    processID: str
    type: str
    jobID: str
    status: str
    message: str
    created: str
    started: Union[str, None] = None
    finished: Union[str, None] = None
    updated: Union[str, None] = None
    progress: int


class ProcessPayload(BaseModel):
    id: str
    title: str
    description: Union[str, None] = ''
    version: str

    jobControlOptions: list = ['sync-execute']
    outputTransmission: list = ['value']

    additionalParameters: dict
    inputs: dict
    outputs: dict
    definitions: dict = {}
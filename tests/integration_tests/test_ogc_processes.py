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
import os
import time
from unittest import TestCase

import requests
from dotenv import load_dotenv
from jsonschema.validators import validate

from ideas_api.lib.utils.TimeUtlis import TimeUtils

version = f'0.0.1123'


class TestOgcProcesses(TestCase):


    def setUp(self) -> None:
        super().setUp()
        load_dotenv()
        self.token = os.environ.get('auth_token')
        self.base_url = os.environ.get('base_url')
        self.base_url = self.base_url[: -1] if self.base_url.endswith('/') else self.base_url

    def test_create_new_process_01(self):
        # version = f'0.0.{TimeUtils().get_datetime_unix(False)}'
        new_process = {
  "id": "UNIT-TEST:EXAMPLE-API",
  "title": "Process Title",
  "description": "Process Description for LIS and RRR + Rapid. Ref: https://github.com/opengeospatial/ogcapi-processes/blob/master/core/examples/json/ProcessDescription.json",
  "version": version,
  "jobControlOptions": [
    "sync-execute"
  ],
  "outputTransmission": [
    "value"
  ],
  "additionalParameters": {
    "parameters": [
      {
        "name": "stagesCount",
        "value": [
          "2"
        ]
      },
      {
        "name": "stage001Names",
        "value": [
          "LIS"
        ]
      },
      {
        "name": "stage002Names",
        "value": [
          "RRR",
          "RAPID"
        ]
      }
    ]
  },
  "inputs": {
    "executingStageFlags": {
      "title": "mandatory input to describe which stages need to be executed",
      "description": "Boolean array to indicate which stages to be executed. each array index corresponds to each stage which where the details can be found in #/additionalParameters/parameters. If missing or mismatched, a default value of 'TRUE' is used.",
      "schema": {
        "$ref": "#/definitions/executingStageFlagsSchema"
      }
    },
    "stagedResults": {
      "title": "Results from other or input processes",
      "description": "This can be power Process result or LIS process result if starting from RRR",
      "schema": {
        "$ref": "#/definitions/stagedResultsSchema"
      }
    },
    "scenario": {
      "title": "TODO:",
      "description": "TODO:",
      "schema": {
        "type": "string",
        "enum": [
          "1x",
          "2x",
          "3x"
        ]
      }
    },
    "hydroModel": {
      "title": "TODO:",
      "description": "TODO:",
      "schema": {
        "type": "string",
        "enum": [
          "VIC",
          "NOAH"
        ]
      }
    },
    "precipitationType": {
      "title": "TODO:",
      "description": "TODO:",
      "schema": {
        "type": "string",
        "enum": [
          "CHIRPS",
          "MERRA2",
          "IMERG"
        ]
      }
    },
    "basinId": {
      "title": "MERIT-Basin ID",
      "description": "The numerical ID used to denote a MERIT-Basin. Currently only supporting basins 23 (western Europe) and 74 (Mississippi)",
      "schema": {
        "type": "integer",
        "enum": [
          23,
          74
        ]
      }
    },
    "landSurfaceModel": {
      "title": "Land Surface Model",
      "description": "Land Surface Model used as input data for RAPID.",
      "schema": {
        "type": "string",
        "enum": [
          "VIC",
          "NOAH",
          "NOAH_MP_1x",
          "NOAH_MP_2x",
          "NOAH_MP_3x",
          "CLSM",
          "LIS"
        ]
      }
    },
    "spatialResolution": {
      "title": "TODO:",
      "description": "TODO:. Example: 1, 2, 3, ...",
      "schema": {
        "type": "string"
      }
    },
    "startTime": {
      "title": "start time for the process",
      "description": "start time for the process in date-time string",
      "schema": {
        "type": "string",
        "format": "date-time"
      }
    },
    "endTime": {
      "title": "end time for the process",
      "description": "end time for the process in date-time string",
      "schema": {
        "type": "string",
        "format": "date-time"
      }
    },
    "spatialCoverage": {
      "title": "spatial coverage to be used for all the processes",
      "description": "Bounding box is the only supported spatial coverage type for this workflow",
      "schema": {
        "$ref": "#/definitions/spatialCoverageSchema"
      }
    }
  },
  "outputs": {
    "processResults": {
      "title": "Results from each stage in the workflow",
      "description": "This can be power Process result or LIS process result if starting from RRR",
      "schema": {
        "type": "array",
        "items": {
          "$ref": "#/definitions/processResultsSchema"
        }
      }
    }
  },
  "definitions": {
    "executingStageFlagsSchema": {
      "type": "array",
      "description": "This is an array to describe whether to execute each stage of the workflow. As this workflow as 2 stages, the length is 2.",
      "minItems": 2,
      "maxItems": 2,
      "items": {
        "type": "boolean"
      }
    },
    "stagedResultsSchema": {
      "type": "array",
      "description": "This is where previous and external stage results will be added so that they can be used in current workflow. ",
      "items": {
        "type": "object",
        "required": [
          "name",
          "value"
        ],
        "properties": {
          "name": {
            "type": "string",
            "description": "It is the name of the stage. a specific datatype can be appended if needed. example: LIS___data"
          },
          "value": {
            "type": "string",
            "description": "usualy a URL like S3 URL where the file is stored"
          }
        }
      }
    },
    "spatialCoverageSchema": {
      "type": "object",
      "description": "This is the OGC definition of bbox. Pls follow this definition when providing bbox as an input",
      "required": [
        "bbox"
      ],
      "properties": {
        "bbox": {
          "bbox": {
            "type": "array",
            "oneOf": [
              {
                "maxItems": 4,
                "minItems": 4,
                "type": "object"
              },
              {
                "maxItems": 6,
                "minItems": 6,
                "type": "object"
              }
            ],
            "items": {
              "type": "number"
            }
          },
          "crs": {
            "type": "string",
            "format": "uri",
            "default": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
            "enum": [
              "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
              "http://www.opengis.net/def/crs/OGC/0/CRS84h"
            ]
          }
        }
      }
    },
    "processResultsSchema": {
      "type": "object",
      "description": "This is how outputs from each stage is stored",
      "required": [
        "name",
        "value"
      ],
      "properties": {
        "name": {
          "type": "string",
          "description": "It is the name of the stage. a specific datatype can be appended if needed. example: LIS___data"
        },
        "value": {
          "type": "string",
          "description": "usualy a URL like S3 URL where the file is stored"
        }
      }
    }
  },
  "links": [
    {
      "href": "https://processing.example.org/oapi-p/processes/EchoProcess/execution",
      "rel": "http://www.opengis.net/def/rel/ogc/1.0/execute",
      "title": "Execute endpoint"
    }
  ]
}
        headers = {
          'Authorization': f'Bearer {self.token}',
          'Content-Type': 'application/json'
        }
        s = requests.session()
        s.trust_env = False
        response = s.put(f'{self.base_url}/processes', data=json.dumps(new_process), headers=headers)
        self.assertEqual(response.status_code, 200)
        return

    def test_list_all_processes_01(self):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        s = requests.session()
        s.trust_env = False
        response = s.get(f'{self.base_url}/processes', headers=headers)
        self.assertEqual(response.status_code, 200)
        print(json.dumps(json.loads(response.text), indent=4))
        return

    def test_get_process_01(self):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        s = requests.session()
        s.trust_env = False
        response = s.get(f'{self.base_url}/processes/UNIT-TEST:EXAMPLE-API?version_id={version}', headers=headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.text)
        print(json.dumps(response_json, indent=2))
        return

    def test_start_job_01(self):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        new_job = {
            "inputs": {
                "executingStageFlags": [
                    True,  # LIS
                    True,  # RRR, Rapid
                ],
                "stagedResults": [
                    # {
                    #     "name": "LIS__DATA",
                    #     "value": "s3://aqacf-nexus-stage/LIS_gar_gdas_3x_3hr/"
                    # }
                ],
                "scenario": "3x",
                "hydroModel": "NOAH",
                "basinId": 23,  # TODO need to be in descriptive string form
                "precipitationType": "GDAS",
                "landSurfaceModel": "LIS",
                "spatialResolution": "1",
                "startTime": "2021-01-01T00:00:00+00:00",
                "endTime": "2021-03-01T00:00:00+00:00",
                "spatialCoverage": {
                    "bbox": [
                        -180.0,
                        -90.0,
                        180.0,
                        90.0
                    ]
                }
            }
        }
        s = requests.session()
        s.trust_env = False
        response = s.post(f'{self.base_url}/processes/UNIT-TEST:EXAMPLE-API/execution?version_id={version}',
                                headers=headers, data=json.dumps(new_job))
        self.assertEqual(response.status_code, 200, response.text)
        response_json = json.loads(response.text)
        created_job_schema = {
            "type": "object",
            "required": ["processID", "type", "jobID", "status", "message", "progress"],
            "properties": {
                "processID": {"type": "string"},
                "type": {"type": "string", "enum": ["process"]},
                "jobID": {"type": "string"},
                "status": {"type": "string", "enum": ["ACCEPTED"]},
                "message": {"type": "string"},
                "progress": {"type": "integer"},
            }
        }
        try:
            validate(instance=response_json, schema=created_job_schema)
        except Exception as errors:
            self.assertTrue(False, f'failed to validate response against schema: {response_json} vs. {errors}')
        time.sleep(5)
        response = requests.get(f'{self.base_url}/jobs/{response_json["jobID"]}', headers=headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.text)
        status_job_schema = {
            "type": "object",
            "required": ["processID", "type", "jobID", "status", "message", "created", "progress"],
            "properties": {
                "processID": {"type": "string"},
                "type": {"type": "string", "enum": ["process"]},
                "jobID": {"type": "string"},
                "status": {"type": "string", "enum": ["ACCEPTED", 'RUNNING', 'SUCCESSFUL', 'FAILED', 'DISMISSED']},
                "message": {"type": "string"},
                "created": {"type": "string"},
                "started": {"type": "string"},
                "finished": {"type": "string"},
                "updated": {"type": "string"},
                "progress": {"type": "integer"},
            }
        }
        try:
            validate(instance=response_json, schema=status_job_schema)
        except Exception as errors:
            self.assertTrue(False, f'failed to validate status response against schema: {response_json} vs. {errors}')
        return

    def test_result_job_01(self):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        s = requests.session()
        s.trust_env = False
        response = s.get(f'{self.base_url}/jobs/a6779174-cd35-4598-8792-a12ca074f8fe-2023-11-07T22:43:21.399767/results', headers=headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.text)
        print(response.text)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.text)
        result_job_schema = {
            "type": "object",
            "required": ["processResults"],
            "properties": {
                "processResults": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "value"],
                        "properties": {
                            "name": {"type": "string"},
                            "value": {"type": "string"},
                        }
                    }
                },
            }
        }
        try:
            validate(instance=response_json, schema=result_job_schema)
        except Exception as errors:
            self.assertTrue(False, f'failed to validate status response against schema: {response_json} vs. {errors}')
        return

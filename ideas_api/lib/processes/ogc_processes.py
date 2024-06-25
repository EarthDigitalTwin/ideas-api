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
from typing import Union
from uuid import uuid4

from jsonschema.validators import validate
from pydantic import BaseModel

from ideas_api.lib.external_io.es_abstract import ESAbstract
from ideas_api.lib.external_io.pub_sub_abstract import PubSubAbstract
from ideas_api.lib.job_management.job_constants import JobConstants
from ideas_api.lib.ogc_processes.process_schema import process_schema
from ideas_api.lib.utils.TimeUtlis import TimeUtils
from ideas_api.lib.utils.parallel_json_validator import SingleJsonValidator

LOGGER = logging.getLogger(__name__)






class OgcProcess:
    def __init__(self, es_middleware: ESAbstract, pub_sub: PubSubAbstract):
        self.__es_middleware = es_middleware
        self.__pub_sub = pub_sub

    def get_all_processes(self):
        process_results = self.__es_middleware.query_pages({
            '_source': ['id', 'version', 'title', 'description'],
            'query': {
                'bool': {
                    'must': [{'match_all': {}}]
                }
            },
            'sort': [{'id': {'order': 'asc'}}],
        }, querying_index=JobConstants.OGC_PROCESS_INDEX_ALIAS)
        return [k['_source'] for k in process_results['hits']['hits']]

    def get_single_process(self, process_id: str, version=''):
        dsl_query = {
            'size': 1000,
            'query': {
                'bool': {'must': [
                    {'term': {'id': {'value': process_id}}}
                ]}
            },
            'sort': [{'version': {'order': 'desc'}}],
        }
        if version != '':
            dsl_query['query']['bool']['must'].append({'term': {'version': {'value': version}}})
        process_results = self.__es_middleware.query(dsl_query, querying_index=JobConstants.OGC_PROCESS_INDEX_ALIAS)
        if len(process_results['hits']['hits']) < 1:
            raise ValueError(f'no such process: {process_id}, optional version: {version}')
        return process_results['hits']['hits'][0]['_source']

    def create_new_instance(self, process_id: str, new_job: dict, version=''):
        process_details = self.get_single_process(process_id, version)
        process_inputs = process_details['inputs']
        validation_errors = {}
        for k, v in new_job['inputs'].items():
            if k not in process_inputs:
                validation_errors[k] = {'message': f'not defined in process details: {process_id}___{version}'}
            else:
                temp_schema = process_inputs[k]
                temp_schema['definitions'] = process_details['definitions']
                validation_result, validation_details = SingleJsonValidator().load_schema(temp_schema).validate(v)
                if validation_result is False:
                    validation_errors[k] = {
                        'message': 'validation failed',
                        'details': validation_details,
                        'schema': temp_schema,
                    }
        if len(validation_errors) > 0:
            raise ValueError(f'one or more keys are not valid. {validation_errors}')
        ingesting_dict = {
            'processID': process_details['id'],
            'processVersion': process_details['version'],
            'jobID': f'{uuid4()}-{TimeUtils.get_current_time()}',
            'job': new_job,
            'created': int(TimeUtils().get_datetime_unix(False)),
            'started': -999,
            'finished': -999,
            'updated': -999,
            'progress': 0,
            'status': 'ACCEPTED',
            'type': 'process',  # hardcoded for now.
            'message': '',
            'outputs': [],
        }
        job_started_msg = {
            'messageType': 'RESULT',
            'jobID': ingesting_dict['jobID'],
            'status': 'SUCCESSFUL',
            'stage': JobConstants.PRE_PROCESSED,
            'message': 'Requesting to start this job',
        }
        self.__es_middleware.index_one(ingesting_dict, ingesting_dict['jobID'], JobConstants.OGC_JOB_INDEX_ALIAS)
        self.__pub_sub.publish_msg(json.dumps(job_started_msg))
        response_dict = {
            'processID': process_details['id'],
            'type': 'process',
            'jobID': ingesting_dict['jobID'],
            'status': 'ACCEPTED',
            'message': '',
            'created': ingesting_dict['created'],
            'progress': ingesting_dict['progress'],
        }
        return response_dict

    def create_new_process(self, new_process: dict):
        try:
            validate(instance=new_process, schema=process_schema)
        except Exception as errors:
            raise ValueError(f'failed to validate incoming process against schema: {errors}')
        self.__es_middleware.index_one(new_process, f"{new_process['id']}___{new_process['version']}", JobConstants.OGC_PROCESS_INDEX_ALIAS)
        return self

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

from fastapi import HTTPException

from ideas_api.lib.external_io.es_abstract import ESAbstract
from ideas_api.lib.job_management.job_constants import JobConstants
from ideas_api.lib.utils.TimeUtlis import TimeUtils
from ideas_api.lib.utils.config import Config

LOGGER = logging.getLogger(__name__)


class OgcJobs:
    def __init__(self, es_middleware: ESAbstract):
        self.__es_middleware = es_middleware

    def get_job_raw(self, job_id: str):
        dsl_query = {
            'size': 1000,
            'query': {
                'bool': {'must': [
                    {'term': {'jobID': job_id}}
                ]}
            },
            'sort': [{'jobID': {'order': 'desc'}}],
        }
        job_results = self.__es_middleware.query(dsl_query, querying_index=JobConstants.OGC_JOB_INDEX_ALIAS)
        if len(job_results['hits']['hits']) < 1:
            raise ValueError(f'no such job: {job_id}')
        return job_results['hits']['hits'][0]['_source']

    def get_job_status(self, job_id: str):
        try:
            job_detail = self.get_job_raw(job_id)
            response_json_model = {
              "processID": job_detail['processID'],
              "type": job_detail['type'],
              "jobID": job_detail['jobID'],
              "status": job_detail['status'],
              "message": job_detail['message'],
              "created": TimeUtils().parse_from_unix(job_detail['created'], False).get_datetime_str(in_ms=False),
              "started": TimeUtils().parse_from_unix(job_detail['started'], False).get_datetime_str(in_ms=False),
              "finished": TimeUtils().parse_from_unix(job_detail['finished'], False).get_datetime_str(in_ms=False),
              "updated": TimeUtils().parse_from_unix(job_detail['updated'], False).get_datetime_str(in_ms=False),
              "progress": job_detail['progress'],
            }
        except Exception as e:
            LOGGER.exception('failed to get a raw job')
            raise HTTPException(status_code=500, detail=str(e))
        return response_json_model

    def get_cached_stage_output(self, cached_job, checking_stage):
        print(f'cached_job: {cached_job}')
        cached_results = []
        if cached_job is None:
            return cached_results
        if 'job' not in cached_job or 'outputs' not in cached_job['job']:
            return cached_results
        for each in cached_job['job']['outputs']:
            if each['name'].startswith(checking_stage):
                cached_results.append(each)
        return cached_results

    def get_cached_result(self, ingesting_dict: dict):
        existing_jobs = self.get_existing_same_jobs(ingesting_dict['processID'], ingesting_dict['processVersion'], ingesting_dict['jobID'], int(Config().get_value(Config.CACHING_JOBS, Config.DEFAULT_CONFIG_JOBS)))
        ingesting_dict = ingesting_dict['job']['inputs']
        for each_existing_job in existing_jobs:
            each_existing_job_inputs = each_existing_job['job']['inputs']
            if each_existing_job_inputs == ingesting_dict:  # current assumption is everything must be the same. executing jobs. ancillary process results and other params.
                return each_existing_job
        return None

    def get_existing_same_jobs(self, process_id: str, process_version: str, job_id: str, number_of_jobs:int = 100):
        dsl_query = {
            'size': number_of_jobs,
            'query': {
                'bool': {'must': [
                    {'term': {'processID': process_id}},
                    {'term': {'processVersion': process_version}},
                    {'bool': {'must_not': [
                        {'term': {'jobID': job_id}},
                        {'term': {'finished': -999}},
                    ]}}
                ]}
            },
            'sort': [{'started': {'order': 'desc'}}],
        }
        job_results = self.__es_middleware.query(dsl_query, querying_index=JobConstants.OGC_JOB_INDEX_ALIAS)
        if len(job_results['hits']['hits']) < 1:
            return []
        return [k['_source'] for k in job_results['hits']['hits']]

    def get_job_result(self, job_id: str):
        job_detail = self.get_job_raw(job_id)
        if 'job' in job_detail and 'outputs' in job_detail['job']:
            return {
                'processResults': job_detail['job']['outputs']
            }
        raise HTTPException(status_code=500, detail=f'unable to find processResults for {job_id}')

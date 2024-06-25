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
from uuid import uuid4

from ideas_api.lib.external_io.es_abstract import ESAbstract
from ideas_api.lib.external_io.pub_sub_abstract import PubSubAbstract
from ideas_api.lib.job_management.job_constants import JobConstants
from ideas_api.lib.processes.ogc_jobs import OgcJobs
from ideas_api.lib.processes.ogc_process_stages import OgcProcessStages
from ideas_api.lib.processes.ogc_processes import OgcProcess
from ideas_api.lib.utils.TimeUtlis import TimeUtils
from ideas_api.lib.utils.parallel_json_validator import SingleJsonValidator

LOGGER = logging.getLogger(__name__)

BASIC_MSG_SCHEMA = {
    'type': 'object',
    'required': ['jobID', 'messageType'],
    'properties': {
        'jobID': {'type': 'string'},
        'messageType': {
            'type': 'string',
            'enum': ['UPDATE', 'RESULT'],
        },
    }
}
UPDATE_MSG_SCHEMA = {  #  not including ['jobID', 'messageType']. They are assumed to be validated in previous step
    'type': 'object',
    'required': ['stage', 'status', 'message'],
    'properties': {
        'stage': {'type': 'string'},
        'message': {'type': 'string'},
        'status': {
            'type': 'string',
            'enum': ['RUNNING'],
        },
    }
}
RESULT_MSG_SCHEMA = {
    'type': 'object',
    'required': ['stage', 'status'],
    'properties': {
        'stage': {'type': 'string'},
        'message': {'type': 'string'},
        'status': {
            'type': 'string',
            'enum': ['SUCCESSFUL', 'FAILED'],
        },
        'outputs': {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['name', 'value'],
                'properties': {
                    'name': {
                        'type': 'string',
                        'enum': ['DATA', 'METADATA', 'ANCILLARY']
                    },  # TODO more data types?
                    'value': {'type': 'string'},  # TODO URL only
                }
            }
        }
    }
}


class OgcJobUpdater:
    def __init__(self, es_middleware: ESAbstract, pub_sub: PubSubAbstract):
        self.__es_middleware = es_middleware
        self.__pub_sub = pub_sub
        self.__job_id = ''
        self.__job_details = None
        self.__sns_msg = None
        self.__process_def = None
        self.__process_stages = OgcProcessStages()

    def __increase_progress(self):
        step_start, step_end = self.__process_stages.get_process_range(self.__sns_msg['stage'])
        current_progress = self.__job_details['progress']
        if current_progress >= step_end:
            return step_end
        one_percent = (step_end - step_start) * 0.01
        new_progress = current_progress + one_percent
        while new_progress >= step_end:
            one_percent *= 0.5
            new_progress = current_progress + one_percent
        return new_progress

    def __execute_update(self):
        validation_result, validation_details = SingleJsonValidator().load_schema(UPDATE_MSG_SCHEMA).validate(self.__sns_msg)
        if not validation_result:
            raise ValueError(f'invalid update sns msg: {validation_details}')


        job_details_updating_dict = {
            'message': f"{self.__sns_msg['stage']}:: {self.__sns_msg['message']}",
            'progress': self.__increase_progress(),
            'updated': TimeUtils().get_datetime_unix(False),
        }
        job_logs_dict = {
            'jobID': self.__job_id,
            'message': self.__sns_msg['message'],
            'stage': self.__sns_msg['stage'],
            'updated': TimeUtils().get_datetime_unix(False),
        }
        self.__es_middleware.update_one(job_details_updating_dict, self.__job_id, JobConstants.OGC_JOB_INDEX_ALIAS)
        self.__es_middleware.index_one(job_logs_dict, f'{uuid4()}', JobConstants.OGC_JOB_LOGS_INDEX_ALIAS)
        return self

    def __execute_result(self):
        """
        if stage is pre-process,
            don't care about result (it's always successful). or double check
            progress = 1
            status = started
            started = current time
            updated = always latest time
            message = ???
        if not.
        if result is successful,
            progress = updated it. TODO
            result = append it
            updated = always latest time
            message = ???
            check if there is next step.
                if so, execute it
                if not, status = successful
        if result is failed,
            progress = 100 ??
            status = failure
            message = error message.


        Steps:
        validate result ?
            failed: throw error.
        Log it
        Job status ?
            failed: update DB.
            quit
        Job status = successful.
        Has outputs?
            no output: update DB.
            quit
        get next stage ?
            finished: update DB.
            quit
        >>>>>
        latest cached job.
        if next stage is finished there,
        copy result to output.
        get next stage again
            till there is no result.
        <<<<<
        starting next stage
            current stage = pre-processed
        :return:
        """
        validation_result, validation_details = SingleJsonValidator().load_schema(RESULT_MSG_SCHEMA).validate(
            self.__sns_msg)
        if not validation_result:
            raise ValueError(f'invalid result sns msg: {validation_details}')
        sns_msg = self.__sns_msg['message'] if 'message' in self.__sns_msg else ''
        job_result_array = self.__job_details['job']['outputs'] if 'outputs' in self.__job_details['job'] else []
        if 'outputs' in self.__sns_msg:
            for each in self.__sns_msg['outputs']:
                each['name'] = f'{self.__sns_msg["stage"]}__{each["name"]}'
            job_result_array = job_result_array + self.__sns_msg['outputs']
        # log it that current job is done with status.
        job_logs_dict = {
            'jobID': self.__job_id,
            'message': f"finished:: {self.__sns_msg['status']}:: {sns_msg}",
            'stage': self.__sns_msg['stage'],
            'updated': TimeUtils().get_datetime_unix(False),
        }
        self.__es_middleware.index_one(job_logs_dict, f'{uuid4()}', JobConstants.OGC_JOB_LOGS_INDEX_ALIAS)
        # status is failed? update the job details. quit it.
        if self.__sns_msg['status'] == 'FAILED':
            step_start, step_end = self.__process_stages.get_process_range(self.__sns_msg['stage'])
            job_details_updating_dict = {
                'message': f"{self.__sns_msg['stage']}:: {sns_msg}",
                'status': 'FAILED',
                'progress': step_end,
                'finished': TimeUtils().get_datetime_unix(False),
                'job': {
                    'outputs': job_result_array,
                }
            }
            self.__es_middleware.update_one(job_details_updating_dict, self.__job_id, JobConstants.OGC_JOB_INDEX_ALIAS)
            return self
        # status is successful...
        if 'outputs' not in self.__sns_msg and self.__sns_msg['stage'] != JobConstants.PRE_PROCESSED:
            step_start, step_end = self.__process_stages.get_process_range(self.__sns_msg['stage'])
            job_details_updating_dict = {
                'message': f"{self.__sns_msg['stage']}:: missing outputs",
                'status': 'FAILED',
                'progress': step_end,
                'finished': TimeUtils().get_datetime_unix(False),
                'job': {
                    'outputs': job_result_array,
                }
            }
            self.__es_middleware.update_one(job_details_updating_dict, self.__job_id, JobConstants.OGC_JOB_INDEX_ALIAS)
            raise ValueError(f'missing output in successful result message: {self.__sns_msg}')
        # find next step
        ogc_jobs = OgcJobs(self.__es_middleware)
        cached_job = ogc_jobs.get_cached_result(self.__job_details)
        next_step = self.__process_stages.get_next_process(self.__sns_msg['stage'], self.__job_details['job']['inputs']['executingStageFlags'])

        if next_step == JobConstants.FINISHED:
            job_details_updating_dict = {
                'message': f"{self.__sns_msg['stage']}:: {sns_msg}",
                'status': 'SUCCESSFUL',
                'progress': 100,
                'finished': TimeUtils().get_datetime_unix(False),
                'job': {
                    'outputs': job_result_array,
                }
            }
            self.__es_middleware.update_one(job_details_updating_dict, self.__job_id, JobConstants.OGC_JOB_INDEX_ALIAS)
            return self
        step_start, step_end = self.__process_stages.get_process_range(next_step)

        cached_result = ogc_jobs.get_cached_stage_output(cached_job, next_step)
        while len(cached_result) > 0:
            job_logs_dict = {
                'jobID': self.__job_id,
                'message': f"found cached result",
                'stage': next_step,
                'updated': TimeUtils().get_datetime_unix(False),
            }
            self.__es_middleware.index_one(job_logs_dict, f'{uuid4()}', JobConstants.OGC_JOB_LOGS_INDEX_ALIAS)
            job_result_array = job_result_array + cached_result
            # TODO not sure this is need to be updated repeatedly
            job_details_updating_dict = {
                'message': f"{next_step}:: cached",
                'progress': step_end,
                'updated': TimeUtils().get_datetime_unix(False),
                'job': {
                    'outputs': job_result_array,
                }
            }
            self.__es_middleware.update_one(job_details_updating_dict, self.__job_id, JobConstants.OGC_JOB_INDEX_ALIAS)
            next_step = self.__process_stages.get_next_process(next_step, self.__job_details['job']['inputs']['executingStageFlags'])
            if next_step == JobConstants.FINISHED:
                job_details_updating_dict = {
                    'message': f"{self.__sns_msg['stage']}:: {sns_msg}",
                    'status': 'SUCCESSFUL',
                    'progress': 100,
                    'finished': TimeUtils().get_datetime_unix(False),
                    'job': {
                        'outputs': job_result_array,
                    }
                }
                self.__es_middleware.update_one(job_details_updating_dict, self.__job_id,
                                                JobConstants.OGC_JOB_INDEX_ALIAS)
                return self
            step_start, step_end = self.__process_stages.get_process_range(next_step)
            cached_result = ogc_jobs.get_cached_stage_output(cached_job, next_step)

        # TODO check if the job already exists.. if so, check if each stage is already executed. Then, update and move on.
        # store result to job details
        job_details_updating_dict = {
            'message': f"{next_step}:: starting",
            'progress': step_start,
            'updated': TimeUtils().get_datetime_unix(False),
            'job': {
                    'outputs': job_result_array,
                }
        }
        if self.__sns_msg['stage'] == JobConstants.PRE_PROCESSED:
            job_details_updating_dict['status'] = 'RUNNING'
            job_details_updating_dict['started'] = job_details_updating_dict['updated']
        self.__es_middleware.update_one(job_details_updating_dict, self.__job_id, JobConstants.OGC_JOB_INDEX_ALIAS)

        # store update message.
        job_logs_dict = {
            'jobID': self.__job_id,
            'message': f"starting",
            'stage': next_step,
            'updated': TimeUtils().get_datetime_unix(False),
        }
        self.__es_middleware.index_one(job_logs_dict, f'{uuid4()}', JobConstants.OGC_JOB_LOGS_INDEX_ALIAS)

        # trigger next step
        job_started_msg = {
            'messageType': 'REQUEST',
            'jobID': self.__job_id,
            'stage': next_step,
            'inputs': self.__job_details['job']['inputs'],
            'current_outputs': job_result_array,
        }
        self.__pub_sub.publish_msg(json.dumps(job_started_msg))
        return self

    def process_update(self, sns_msg: dict):
        validation_result, validation_details = SingleJsonValidator().load_schema(BASIC_MSG_SCHEMA).validate(sns_msg)
        if not validation_result:
            raise ValueError(f'invalid sns msg: {validation_details}')
        self.__job_id = sns_msg['jobID']
        self.__job_details = OgcJobs(self.__es_middleware).get_job_raw(self.__job_id)  # this will throw an error if not found
        self.__sns_msg = sns_msg
        self.__process_def = OgcProcess(self.__es_middleware, self.__pub_sub).get_single_process(  # this will throw an error if not found
            self.__job_details['processID'],
            self.__job_details['processVersion'],
        )
        self.__process_stages.setup(self.__process_def)
        if sns_msg['messageType'] == 'UPDATE':
            return self.__execute_update()
        if sns_msg['messageType'] == 'RESULT':
            return self.__execute_result()
        raise ValueError(f'invalid messageType: {sns_msg["messageType"]}')

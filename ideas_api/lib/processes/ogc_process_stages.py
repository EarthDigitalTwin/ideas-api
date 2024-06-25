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

from ideas_api.lib.job_management.job_constants import JobConstants
from ideas_api.lib.utils.parallel_json_validator import SingleJsonValidator

LOGGER = logging.getLogger(__name__)
PROCESS_STAGES_SCHEMA = {
    'type': 'object',
    'required': ['additionalParameters'],
    'properties': {
        'additionalParameters': {
        'type': 'object',
        'required': ['parameters'],
        'properties': {
            'parameters': {
                'type': 'array',
                'minItems': 1,
                'items': {
                    'type': 'object',
                    'required': ['name', 'value'],
                    'properties': {
                        'name': {'type': 'string'},
                        'value': {
                            'type': 'array',
                            'minItems': 1,
                            'items': {
                                'type': 'string'
                            }
                        },
                    }
                }
            }
        }
    }
    }
}


class OgcProcessStages:
    def __init__(self):
        self.__total_stages = -1
        self.__stages_dict = {}
        self.__sub_process_dict = {}

    def setup(self, process_def: dict):
        validation_result, validation_details = SingleJsonValidator().load_schema(PROCESS_STAGES_SCHEMA).validate(process_def)
        if not validation_result:
            raise ValueError(f'invalid PROCESS_STAGES_SCHEMA: {validation_details}')
        self.__stages_dict = {k['name']: k['value'] for k in process_def['additionalParameters']['parameters']}
        if 'stagesCount' not in self.__stages_dict:
            raise ValueError(f'invalid process definition. missing key-value pair: stagesCount')
        self.__total_stages = int(self.__stages_dict['stagesCount'][0])
        stage_errors = []
        sub_process_counter = 1
        for i in range(1, self.__total_stages + 1):
            stage_name = f"stage{i:03d}Names"
            if stage_name not in self.__stages_dict:
                stage_errors.append(f'invalid process definition. missing key-value pair: {stage_name}')
                continue
            if not isinstance(self.__stages_dict[stage_name], list) or len(self.__stages_dict[stage_name]) < 1:
                stage_errors.append(f'invalid process definition. empty list for {stage_name}')
                continue
            for j, sub_process_name in enumerate(self.__stages_dict[stage_name]):
                if sub_process_name in self.__sub_process_dict:
                    stage_errors.append(f'duplicate sub_process_name: {sub_process_name} in {stage_name}')
                self.__sub_process_dict[sub_process_name] = {
                    'stage_counter': i,
                    'stage_step': j,
                    'sub_process_counter': sub_process_counter,
                }
                sub_process_counter += 1
        if len(stage_errors) > 0:
            raise ValueError(f'one or more errors: {stage_errors}')
        return self

    def get_process_range(self, current_sub_process: str):
        if current_sub_process not in self.__sub_process_dict:
            raise ValueError(f'unknown sub process name: {current_sub_process}')
        sub_process_counter = self.__sub_process_dict[current_sub_process]['sub_process_counter']
        stage_range = divmod(100, len(self.__sub_process_dict))[0]
        start_range = (stage_range * sub_process_counter) - (stage_range - 1)
        end_range = stage_range * sub_process_counter
        return start_range, end_range

    def get_next_process(self, current_sub_process: str, job_stages_flag: list):  # , job_stages_flag: list
        if len(job_stages_flag) != self.__total_stages:
            raise ValueError(f'job_stages_flag does not match total_stages: {job_stages_flag} v. {self.__total_stages}')
        if current_sub_process == JobConstants.PRE_PROCESSED:
            for i in range(self.__total_stages):
                if job_stages_flag[i] is False:
                    continue
                return self.__stages_dict[f'stage{i+1:03d}Names'][0]
            return JobConstants.FINISHED
        if current_sub_process not in self.__sub_process_dict:
            raise ValueError(f'missing sub_process: {current_sub_process}')
        next_stage_step = self.__sub_process_dict[current_sub_process]['stage_step'] + 1
        current_stage_name = f"stage{self.__sub_process_dict[current_sub_process]['stage_counter']:03d}Names"
        if len(self.__stages_dict[current_stage_name]) > next_stage_step:  # same stage. no need to check the flag.
            return self.__stages_dict[current_stage_name][next_stage_step]

        next_stage_counter = self.__sub_process_dict[current_sub_process]['stage_counter']
        if next_stage_counter >= self.__total_stages:
            return JobConstants.FINISHED
        for i in range(next_stage_counter, self.__total_stages):
            if job_stages_flag[i] is False:
                continue
            return self.__stages_dict[f'stage{i + 1:03d}Names'][0]
        return JobConstants.FINISHED

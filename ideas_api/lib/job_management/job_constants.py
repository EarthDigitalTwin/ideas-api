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

class JobConstants:
    OGC_PROCESS_INDEX_ALIAS = 'ogc_process'
    OGC_JOB_INDEX_ALIAS = 'ogc_job'
    OGC_JOB_LOGS_INDEX_ALIAS = 'ogc_job_logs'

    PROCESSES = 'processes'
    JOBS = 'jobs'
    JOB_INDEX_ALIAS = 'jobs'
    JOB_STEPS = ['PRE_PROCESSED', 'LIS', 'RRR', 'RAPID', 'POWER']
    PRE_PROCESSED = 'PRE_PROCESSED'
    FINISHED = 'FINISHED'
    JOB_STATUS_NA = 'NA'
    JOB_STATUS_QUEUED = 'QUEUED'
    JOB_STATUS_IN_PROGRESS = 'IN_PROGRESS'
    JOB_STATUS_SUCCESS = 'SUCCESSFUL'
    JOB_STATUS_FAILURE = 'FAILED'

    JOB_MSG_TYPE_REQUEST = 'job_request'
    JOB_MSG_TYPE_RESULT = 'job_result'

    JOB_API_ENDPOINT = '/job'
    JOB_API_PREFIX = ''


class SnsMsgConstants:
    JOB_STEP = 'job_step'
    JOB_STATUS = 'job_status'
    JOB_ID = 'job_id'
    MSG_TYPE = 'message_type'
    DETAILED_MSG = 'detailed_msg'
    JOB_OUTPUT = 'job_output'
    JOB_INPUT = 'job_input'


OGC_PROCESS_MAPPING = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "keyword"},
            "version": {"type": "keyword"},
        }
    }
}

OGC_JOB_MAPPING = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2
    },
    "mappings": {
        "properties": {
            "processID": {"type": "keyword"},
            "processVersion": {"type": "keyword"},
            "jobID": {"type": "keyword"},
            "status": {"type": "keyword"},
            "progress": {"type": "integer"},
            "created": {"type": "long"},
            "started": {"type": "long"},
            "finished": {"type": "long"},
            "updated": {"type": "long"},
        }
    }
}

JOB_STAGE_LOGS_MAPPING = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2
    },
    "mappings": {
        "properties": {
            "jobID": {"type": "keyword"},
            "messageType": {"type": "keyword"},
            "stage": {"type": "keyword"},
            "message": {"type": "text"},
        }
    }
}

JOB_INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2
    },
    "mappings": {
        "properties": {
            "job_id": {"type": "keyword"},
            "job_status": {"type": "keyword"},
            "job_creation_time": {"type": "keyword"},
            "lis_job_status": {"type": "keyword"},
            "rrr_job_status": {"type": "keyword"},
            "rapid_job_status": {"type": "keyword"},
            "power_job_status": {"type": "keyword"}
        }
    }
}

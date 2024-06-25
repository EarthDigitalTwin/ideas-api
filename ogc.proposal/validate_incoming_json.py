import json

from jsonschema.validators import validate

from ideas_api.lib.utils.parallel_json_validator import SingleJsonValidator


def validate_me(json_file_path: str, json_key: str):
    with open('ogc.processes.schema.dict.json', 'r') as ff:
        main_schema = json.loads(ff.read())

    with open(json_file_path, 'r') as ff:
        my_json = json.loads(ff.read())
    try:
        validate(instance=my_json, schema=main_schema[json_key])
        print(f'{json_key} validated.')
    except Exception as errors:
        print(f'{json_key} NOT validated. details: {errors}')
    return


validate_me('ogc.process.storage.json', 'process')
validate_me('ogc.job.request.body.json', 'execute')
validate_me('ogc.job.request.response.json', 'statusInfo')
validate_me('ogc.job.result.json', 'results')
validate_me('ogc.job.status.sample.json', 'statusInfo')


def get_schema_def(entire_json, path):
    split_path = path.split('/')[1:]
    current_dict = entire_json
    for each_key in split_path:
        current_dict = current_dict[each_key]
    return current_dict

def validate_ogc_job_request():
    with open('ogc.process.storage.json', 'r') as ff:
        process_storage = json.loads(ff.read())

    with open('ogc.job.request.body.json', 'r') as ff:
        job_request = json.loads(ff.read())

    job_request_inputs = job_request['inputs']
    for k, v in process_storage['inputs'].items():
        if k in job_request_inputs:
            current_schema = v['schema']
            if '$ref' in current_schema:
                current_schema = get_schema_def(process_storage, current_schema['$ref'])
            try:
                validate(instance=job_request_inputs[k], schema=current_schema)
                print(f'{k} validated.')
            except Exception as errors:
                print(f'{k} NOT validated. details: {errors}')
    return
validate_ogc_job_request()
import requests
import json
from ipywidgets import widgets


def list_processes(base_url, headers):
    s = requests.session()
    s.trust_env = False
    response = s.get(f'{base_url}/processes', headers=headers)
    response_json = json.loads(response.text)
    return response_json


def get_process(base_url, process_id, version, headers):
    s = requests.session()
    s.trust_env = False
    response = s.get(f'{base_url}/processes/{process_id}?version_id={version}', headers=headers)
    response_json = json.loads(response.text)
    return response_json


def post_job(base_url, process_id, version, basin, precip, scenario, start, end, headers):
    new_job = {
        "inputs": {
            "executingStageFlags": [
                False,  # LIS
                True,  # RRR, Rapid
            ],
            "stagedResults": [
                {
                    "name": "LIS__DATA",
                    "value": "s3://aqacf-nexus-stage/LIS_miss_imerg_3x_3hr"
                },
                {
                    "name": "LIS__METADATA",
                    "value": "s3://ideas-lis-out/OUTPUT_4e0b9745-eacb-4a8d-9c31-c5c485e158b2/lis_4e0b9745-eacb-4a8d-9c31-c5c485e158b2.config"
                }
            ],
            "scenario": scenario,
            "hydroModel": "NOAH",
            "basinId": basin,
            "precipitationType": precip,
            "landSurfaceModel": "LIS",
            "spatialResolution": "1",
            "startTime": start.isoformat()+ "+00:00",
            "endTime": end.isoformat()+ "+00:00",
            "spatialCoverage": {
                "bbox": [
                    -117, 27.5, -80, 54
                ]
            }
        }
    }
    s = requests.session()
    s.trust_env = False
    response = s.post(f'{base_url}/processes/{process_id}/execution?version_id={version}',
                      headers=headers, data=json.dumps(new_job))
    response_json = json.loads(response.text)
    job_id = response_json['jobID']
    return job_id


def monitor_job(base_url, job_id, headers):
    s = requests.session()
    s.trust_env = False
    response = s.get(f'{base_url}/jobs/{job_id}', headers=headers)
    response_json = json.loads(response.text)
    return response_json


def get_results(base_url, job_id, headers):
    s = requests.session()
    s.trust_env = False
    response = s.get(f'{base_url}/jobs/{job_id}/results', headers=headers)
    response_json = json.loads(response.text)
    return response_json


def get_job_inputs():
    basin_dropdown = widgets.Dropdown(options=[('Mississippi', 74), ('Garonne', 23)], description='Basin:')
    precip_dropdown = widgets.Dropdown(options=['CHIRPS', 'MERRA2', 'IMERG', 'GDAS', 'SAFRAN', 'ERA5'],
                                       description='Precip:')
    scenario_dropdown = widgets.Dropdown(options=['1x', '2x', '3x'], description='Scenario:')
    start_time_picker = widgets.NaiveDatetimePicker(
        description='Start Time:'
    )
    end_time_picker = widgets.NaiveDatetimePicker(
        description='End Time:'
    )

    display(basin_dropdown, precip_dropdown, scenario_dropdown, start_time_picker, end_time_picker)
    return basin_dropdown, precip_dropdown, scenario_dropdown, start_time_picker, end_time_picker

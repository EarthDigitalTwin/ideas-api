### Restructuring schemas to match OGC processes. 
<img title="OGC Compliant Ideas API" alt="OGC Compliant Ideas API" src="OGC Compliant Ideas API.png">

### User facing Endpoints
#### REST: Process Creation
- There is NO OGC compliant endpoint in [OGC swaggerhub](https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/)
- This endpoint need to be authorized so that only admins.
- The format of Process Description JSON should follow [OGC Process schema](https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/process).
- Example Process Description: https://github.com/opengeospatial/ogcapi-processes/blob/master/core/examples/json/ProcessDescription.json
- This will add new Process Description where 
    - the sub process names and stages are defined in `#/additionalParameters/parameters`.
    - and input keys and the schemas for each keys are defined in `#/inputs`. 
    - There will always be 2 hidden stages `PRE_PROCESSED` and `FINISHED`. 
    - `progress` needs to be within the range `[0 - 100]` by OGC Process definition.
        - It can be divided by number of stages from `#/additionalParameters/parameters/0/value`.
        - Example: 100 / 2 = 50 for each stage
        - Then we can further divide progress for each step of a particular stage if a stage happends to have more than 1. like RRR and Rapid.
        - Example LIS at Stage 1 has progress from 0 to 50
        - RRR at Stage 2 has progress from 51 to 75, and Rapid from 76 to 100. 
- An example of Process Definition JSON is linked in Process Retrieval section.
#### REST (OGC compliant): List Processes
- This will follow OGC compliant endpoint: https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/ProcessList/getProcesses
- This endpoint should return a list of available processes. 
- This is an example response json. [ogc.process.list.json](ogc.process.list.json)
#### REST (OGC compliant): Process Retrieval
- This will follow OGC compliant endpoint: https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/ProcessDescription/getProcessDescription
- In reality, there would be another endpoint to list all processes: https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/ProcessList/getProcesses
- This endpoint should return [OGC Process](https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/process)
- Example: [ogc.process.storage.json](ogc.process.storage.json)
- User will use this JSON to create a new job request JSON.
#### REST(OGC compliant): Job Creation
- This will follow OGC compliant endpoint: https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/Execute/execute
- The request and response format is in the above endpoint.
- The request body JSON should follow : https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/execute
- Example from OGC: https://github.com/opengeospatial/ogcapi-processes/blob/master/core/examples/json/Execute.json
- Example for IDEAS API: [ogc.job.request.body.json](ogc.job.request.body.json) and [ogc.job.request.response.json](ogc.job.request.response.json)
- [sns.result.json](sns.result.json) is sent to the Pub/Sub to start the workflow. 
#### REST(OGC compliant): Job Status
- This will follow OGC compliant endpoint: https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/Status/getStatus
- The request and response format is in the above endpoint.
- Ref: https://github.com/opengeospatial/ogcapi-processes/blob/master/core/examples/json/StatusInfo.json
- Ref: https://github.com/opengeospatial/ogcapi-processes/blob/master/core/examples/json/StatusInfo-dismissed.json
- Example: [ogc.job.status.json](ogc.job.status.json)
#### REST(OGC compliant): Job Result
- This will follow OGC compliant endpoint: https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/Result/getResult
- Ref: https://github.com/opengeospatial/ogcapi-processes/blob/master/core/examples/json/Result.json
- Example: [ogc.job.result.json](ogc.job.result.json)

### Backend Processes
- backend processes are not in OGC Job schema at this moment as they are not exposed to users. 
- But it is beneficial to use OGC Job schema. 
#### PRE_PROCESSED 
- Initial message from `REST(OGC compliant): Job Creation` is `RESULT` type of `PRE_PROCESSED` stage.
#### Job Updater
- It will trigger `Job Updater` to update the job storage JSON in Opensearch. 
- It will examine the job storage to send actual stage `REQUEST` type to Pub/Sub.
- Example: [sns.request.json](sns.request.json)
#### STAGES
- Actual job lambdas will receive the `REQUEST` to start processing. 
- Actual job lambdas may send updates if desired.
- Example: [sns.update.json](sns.update.json)
- Actual job lambdas will send a final message with outputs or error at the end of processing.
- Example: [sns.result.json](sns.result.json)
#### Metadata consideration
- the metadata associated with job outputs can be stored in a file or in a literal JSON string. 
  - example: 

        {
          "outputs": [
              {
                "name": "DATA",
                "value": "s3://<bucket>/<key>"
              },
              {
                "name": "METADATA",
                "value": "s3://<bucket>/<key>"
              }
          ]
        }

        {
          "outputs": [
              {
                "name": "DATA",
                "value": "s3://<bucket>/<key>"
              },
              {
                "name": "METADATA",
                "value": "{"metadata": [{"key": "some-key", "value": "some-value"}]}"
              }
          ]
        }
### Sample use-case
- Admin create a new process (a collection of jobs)
    - `PUT` request to `/processes` with body: [ogc.process.storage.json](ogc.process.storage.json)
- User list all processes
    - `GET` request to `/processes` to list all processes.
    - It returns this JSON. [ogc.process.list.json](ogc.process.list.json)
- User finds a process to run. It retrieves the process details
    - `GET` request to `/processes/{id}`. 
    - It returns the process details json. [ogc.process.storage.json](ogc.process.storage.json)
- User starts an instance of the proces, a job. 
    - `POST` request tp `/processes/{id}/execution` with body: [ogc.job.request.body.json](ogc.job.request.body.json)
    - It returns this JSON. [ogc.job.request.response.json](ogc.job.request.response.json)
- User checks job status.
    - `GET` request to `/jobs/{jobId}`.
    - It returns [ogc.job.status.json](ogc.job.status.json)
- User retrieves job result.
    - `GET` request to `/jobs/{jobId}/results`.
    - It returns [ogc.job.result.json](ogc.job.result.json)
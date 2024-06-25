# IDEAS API
## What is it?
Ideas API interface following OGC Processes for arbitrary backend processes.
## How to Deploy?
Pls refer to [Deployment Guide](./documentation/deployment_guide/README.md) to deploy in AWS
## How to run??
1. Get Authorization Token (JWT Bearer token)
    1. This is out of scope for this project as it depends on IT security policy of the client. 
2. As an admin, create a new process
    1. An example Python call to create a new process can be found in the [integration test](./tests/integration_tests/test_ogc_processes.py##L37)
3. As a user, list all the processes, and get details of an interested process. 
    1. An example Python call to list all processes can be found in the [integration test](./tests/integration_tests/test_ogc_processes.py##L279)
    1. An example Python call to get details of a process can be found in the [integration test](./tests/integration_tests/test_ogc_processes.py##L289)
4. Start a new job
    1. An example Python call to start a new job can be found in the [integration test](./tests/integration_tests/test_ogc_processes.py##L300)
4. Monitor job
    1. An example Python call to monitor current job can be found in the [integration test](./tests/integration_tests/test_ogc_processes.py##L363)
5. Retrieve results
    1. An example Python call to retrieve results can be found in the [integration test](./tests/integration_tests/test_ogc_processes.py##L385)
6. Alternatively, follow [the example Jupyter Notebook](./notebook/IDEAS%20API.ipynb)
## How to test??
### Unit Tests
1. run python tests in [tests/ideas_api](./tests/ideas_api)
### Integration Tests
1. After the system is deployed, create .env using [.env.tpl](./.env.tpl)
2. run python tests in [tests/integration_tests](./tests/integration_tests)
## Accident Secrets Removal
1. Follow these repos to remove the secrets before the release.
    - https://github.com/NASA-AMMOS/slim/tree/detect-secrets-rewrite/docs/guides/software-lifecycle/security/secrets-detection
    - https://nasa-ammos.github.io/slim/docs/guides/software-lifecycle/security/secrets-detection/


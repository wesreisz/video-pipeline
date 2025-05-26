# Git Activity Summary (2025-03-17 to 2025-03-23)

## Commit Log

```
ffb4b1b 2025-03-23 Updated Readme
f83e4cc 2025-03-23 Cleaned up some of the end to end tests
027cfde 2025-03-22 Add the SQS Queue and improved Standardization
d5ccda9 2025-03-21 Segment Lengths Retreived
f53ea52 2025-03-21 Cleanup Ugly Code
461b6d6 2025-03-20 Removed the shared libs
feb305f 2025-03-20 returned to a restore
e29abbe 2025-03-19 Deploy Script running successfully There's alot of cleanup but this is a succesful deployment run of the both modules on the cloud.
b904430 2025-03-19 Added Checking Service Implementating and implemnted shared code.
695b250 2025-03-19 Updated SAM for local testing
7d80ab1 2025-03-19 Added Event bridge and step functions This commit and the one before introduces step functions to orchestrate the workshop. The logic for chunking is not yet implemented. All it does it write to the log Hello World. The next step is to implement a strategy that pulls the chunks from the file and passes that to an embedding service
147a5bb 2025-03-19 Added step function workflow
c0f9c46 2025-03-19 Added new module
9f4f7d3 2025-03-19 Added Chunking module
c42207d 2025-03-19 Created a deploy script to deploy the code changes
1a93d1c 2025-03-19 Added audio_segments to our transcription
2487a09 2025-03-18 Refactor: Removed shared libs
b9dfdd1 2025-03-18 Updated README.md
659d8c1 2025-03-18 REFACTOR: Updated the project structure to isolate by modules
8f4200d 2025-03-18 Added addition unit tests around transcription_service
253155c 2025-03-18 REFACTOR: Removed some dead/legacy code paths
2a67bdf 2025-03-18 Updated the tests to define a rule and integration test
a6a63c9 2025-03-18 BUG: There was an issue in the end to end test. Fixed.```

## Detailed Changes

```
--- ffb4b1b ---
ffb4b1b Updated Readme
 README.md | 269 ++++++++++++++++++++++++--------------------------------------
 1 file changed, 102 insertions(+), 167 deletions(-)

--- f83e4cc ---
f83e4cc Cleaned up some of the end to end tests
 infra/environments/dev/deploy.sh                   |  45 +----
 infra/environments/dev/main.tf                     |   6 +-
 .../specs/features/HERE- troubleshooting.md        |  26 ---
 .../specs/features/14-end2end-test-cleanup.md      | 102 +++++++++++
 tests/e2e/pipeline_e2e_test.py                     | 187 +++++++++++++++------
 5 files changed, 251 insertions(+), 115 deletions(-)

--- 027cfde ---
027cfde Add the SQS Queue and improved Standardization
 .cursor/rules/project-architecture.mdc             |   7 +
 .cursor/rules/python.mdc                           | 165 ++++++++++++++
 .cursor/rules/terraform.mdc                        |   3 +
 infra/environments/dev/deploy.sh                   | 183 ++++++++++++---
 infra/environments/dev/main.tf                     |  79 ++++---
 infra/environments/dev/output.json                 |   1 +
 infra/modules/lambda/outputs.tf                    |   5 +
 infra/modules/sqs/main.tf                          |  39 ++++
 infra/modules/sqs/outputs.tf                       |  14 ++
 infra/modules/sqs/variables.tf                     |   9 +
 modules/chunking-module/README.md                  | 184 +++++++++++++--
 modules/chunking-module/dev-requirements.txt       |   2 +
 .../{2-add-boto4s3.md => 3-add-boto4s3.md}         |   0
 .../chunking-module/specs/features/4-cleanup.md    |  43 ++++
 .../specs/features/5-readiness-check.md            | 186 +++++++++++++++
 modules/chunking-module/specs/features/7-sqs.md    | 151 +++++++++++++
 .../chunking-module/specs/features/8-sqs-tests.md  |  98 ++++++++
 .../specs/features/HERE- troubleshooting.md        |  26 +++
 .../specs/features/NOT_RUN_YET_6-async.md          | 146 ++++++++++++
 .../src/handlers/chunking_handler.py               | 200 +++++++++++++----
 modules/chunking-module/src/utils/error_handler.py |   6 +-
 modules/chunking-module/tests/conftest.py          |  81 +++++++
 .../tests/integration/test_chunking_integration.py | 148 ++++++++++++
 .../tests/unit/test_chunking_handler.py            | 171 ++++++++++++++
 .../src/handlers/transcribe_handler.py             |  60 ++---
 terraform.mdc                                      |  74 ++++++
 tests/e2e/pipeline_e2e_test.py                     | 250 +++++++++------------
 27 files changed, 2017 insertions(+), 314 deletions(-)

--- d5ccda9 ---
d5ccda9 Segment Lengths Retreived
 .../specs/features/2-add-boto4s3.md                |  1 +
 .../src/handlers/chunking_handler.py               | 52 ++++++++++++++--------
 2 files changed, 34 insertions(+), 19 deletions(-)

--- f53ea52 ---
f53ea52 Cleanup Ugly Code
 infra/environments/dev/deploy.sh                   |  14 +-
 modules/chunking-module/local_test.py              | 235 ----------
 modules/chunking-module/pytest.ini                 |   7 -
 .../src/handlers/chunking_handler.py               |  51 ---
 .../src/services/chunking_service.py               | 156 -------
 .../src/services/transcription_loader_service.py   | 289 ------------
 modules/chunking-module/src/utils/s3_utils.py      | 116 -----
 modules/chunking-module/tests/README.md            |  89 ----
 modules/chunking-module/tests/conftest.py          |  28 --
 modules/chunking-module/tests/pytest_chunking.py   | 200 --------
 modules/chunking-module/tests/pytest_s3_utils.py   | 138 ------
 modules/chunking-module/tests/test_chunking.py     | 259 -----------
 .../chunking-module/tests/test_chunking_handler.py | 117 -----
 modules/chunking-module/tests/test_s3_utils.py     | 186 --------
 .../chunking-module/tmp/test_transcription.json    |  54 ---
 .../test_transcribe_handler_integration.py         | 231 ----------
 modules/transcribe-module/tests/test_handlers.py   |   5 +-
 .../tests/test_transcription_service.py            | 502 ---------------------
 18 files changed, 4 insertions(+), 2673 deletions(-)

--- 461b6d6 ---
461b6d6 Removed the shared libs
 .cursor/rules/project-structure.mdc   |  7 +---
 modules/__init__.py                   |  5 ---
 modules/shared_libs/README.md         | 47 ----------------------
 modules/shared_libs/__init__.py       |  5 ---
 modules/shared_libs/requirements.txt  |  2 -
 modules/shared_libs/utils/__init__.py |  7 ----
 modules/shared_libs/utils/s3_utils.py | 74 -----------------------------------
 7 files changed, 2 insertions(+), 145 deletions(-)

--- feb305f ---
feb305f returned to a restore
 modules/chunking-module/pytest.ini             |  3 ++-
 modules/chunking-module/tests/test_chunking.py | 16 ++++++++--------
 modules/chunking-module/tests/test_s3_utils.py | 15 ++++++++++-----
 3 files changed, 20 insertions(+), 14 deletions(-)

--- e29abbe ---
e29abbe Deploy Script running successfully There's alot of cleanup but this is a succesful deployment run of the both modules on the cloud.
 README.md                                          |   5 +
 infra/environments/dev/deploy.sh                   |  37 +-
 modules/chunking-module/pytest.ini                 |   6 +
 .../src/handlers/chunking_handler.py               |  51 +-
 .../src/services/chunking_service.py               |  58 +-
 .../src/services/transcription_loader_service.py   | 193 ++++++-
 modules/chunking-module/src/utils/s3_utils.py      |  50 +-
 modules/chunking-module/tests/README.md            |  89 +++
 modules/chunking-module/tests/conftest.py          |  28 +
 modules/chunking-module/tests/e2e/run_e2e_test.py  | 188 -------
 modules/chunking-module/tests/e2e/run_e2e_test.sh  | 174 ------
 modules/chunking-module/tests/pytest_chunking.py   | 200 +++++++
 modules/chunking-module/tests/pytest_s3_utils.py   | 138 +++++
 modules/chunking-module/tests/test_chunking.py     | 259 +++++++++
 .../chunking-module/tests/test_chunking_handler.py |  26 +-
 modules/chunking-module/tests/test_s3_utils.py     | 181 ++++++
 modules/transcribe-module/README.md                |  14 +-
 modules/transcribe-module/tests/e2e/README.md      | 174 ------
 .../transcribe-module/tests/e2e/run_e2e_test.sh    | 225 --------
 .../tests/e2e/test_pipeline_e2e.py                 | 243 --------
 tests/__init__.py                                  |   0
 tests/e2e/README.md                                | 110 ++++
 tests/e2e/__init__.py                              |   0
 tests/e2e/pipeline_e2e_test.py                     | 616 +++++++++++++++++++++
 tests/e2e/run_e2e_test.sh                          | 163 ++++++
 25 files changed, 2149 insertions(+), 1079 deletions(-)

--- b904430 ---
b904430 Added Checking Service Implementating and implemnted shared code.
 infra/environments/dev/deploy.sh                   |  32 +++-
 modules/__init__.py                                |   5 +
 modules/chunking-module/local_test.py              | 110 ++++++++++++-
 .../src/services/chunking_service.py               |  87 +++++++++-
 .../src/services/transcription_loader_service.py   | 132 +++++++++++++++
 .../chunking-module/tmp/test_transcription.json    |  54 +++++++
 modules/shared_libs/README.md                      |  47 ++++++
 modules/shared_libs/__init__.py                    |   5 +
 modules/shared_libs/requirements.txt               |   2 +
 modules/shared_libs/utils/__init__.py              |   7 +
 modules/shared_libs/utils/s3_utils.py              |  74 +++++++++
 .../src/services/transcription_service.py          | 179 ++++++++++++++-------
 12 files changed, 665 insertions(+), 69 deletions(-)

--- 695b250 ---
695b250 Updated SAM for local testing
 template.yaml | 13 ++++++++++++-
 1 file changed, 12 insertions(+), 1 deletion(-)

--- 7d80ab1 ---
7d80ab1 Added Event bridge and step functions This commit and the one before introduces step functions to orchestrate the workshop. The logic for chunking is not yet implemented. All it does it write to the log Hello World. The next step is to implement a strategy that pulls the chunks from the file and passes that to an embedding service
 infra/environments/dev/main.tf                       | 20 ++------------------
 modules/chunking-module/local_test.py                |  2 +-
 .../chunking-module/src/services/chunking_service.py |  9 ++-------
 modules/chunking-module/tests/e2e/run_e2e_test.sh    |  2 +-
 4 files changed, 6 insertions(+), 27 deletions(-)

--- 147a5bb ---
147a5bb Added step function workflow
 README.md                                          |  68 +++-
 infra/environments/dev/main.tf                     | 367 +++++++++++++++++----
 .../src/handlers/chunking_handler.py               |  19 +-
 .../chunking-module/tests/test_chunking_handler.py |   5 +-
 .../src/handlers/transcribe_handler.py             |  37 ++-
 5 files changed, 420 insertions(+), 76 deletions(-)

--- c0f9c46 ---
c0f9c46 Added new module
 infra/environments/dev/deploy.sh                   |  21 ++-
 modules/chunking-module/local_test.py              | 141 ++++++++++++++++
 .../src/handlers/chunking_handler.py               |  18 +-
 .../src/services/chunking_service.py               |  19 ++-
 modules/chunking-module/tests/e2e/run_e2e_test.py  | 188 +++++++++++++++++++++
 modules/chunking-module/tests/e2e/run_e2e_test.sh  | 174 +++++++++++++++++++
 .../chunking-module/tests/test_chunking_handler.py |   7 +-
 7 files changed, 547 insertions(+), 21 deletions(-)

--- 9f4f7d3 ---
9f4f7d3 Added Chunking module
 infra/environments/dev/deploy.sh                   | 106 ++++++++++++++------
 infra/environments/dev/main.tf                     |  75 +++++++++++++-
 modules/chunking-module/README.md                  | 109 +++++++++++++++++++++
 modules/chunking-module/dev-requirements.txt       |  14 +++
 modules/chunking-module/requirements.txt           |   2 +
 .../specs/features/1-new-module-creation.md        |   7 ++
 .../src/handlers/chunking_handler.py               |  71 ++++++++++++++
 modules/chunking-module/src/models/chunk.py        |  50 ++++++++++
 .../src/services/chunking_service.py               |  29 ++++++
 modules/chunking-module/src/utils/error_handler.py |  34 +++++++
 modules/chunking-module/src/utils/s3_utils.py      |  74 ++++++++++++++
 .../chunking-module/tests/test_chunking_handler.py | 109 +++++++++++++++++++++
 12 files changed, 646 insertions(+), 34 deletions(-)

--- c42207d ---
c42207d Created a deploy script to deploy the code changes
 infra/environments/dev/deploy.sh    | 130 ++++++++++++++++++++++++++++++++++++
 modules/transcribe-module/README.md | 105 ++++++++++++++++++++++-------
 2 files changed, 210 insertions(+), 25 deletions(-)

--- 1a93d1c ---
1a93d1c Added audio_segments to our transcription
 modules/transcribe-module/README.md                |  54 ++++++++-
 .../docs/sentence-level-segments.md                | 120 +++++++++++++++++++
 .../specs/features/13-sentence-refactor.md         |  24 ++++
 .../src/models/transcription_result.py             |  13 +-
 .../src/services/transcription_service.py          | 109 ++++++++++-------
 .../tests/e2e/test_pipeline_e2e.py                 |  14 ++-
 .../tests/test_transcription_service.py            | 132 ++++++++++++++++-----
 7 files changed, 385 insertions(+), 81 deletions(-)

--- 2487a09 ---
2487a09 Refactor: Removed shared libs
 README.md                  | 14 +-------------
 libs/base/requirements.txt |  0
 libs/base/run.sh           | 10 ----------
 3 files changed, 1 insertion(+), 23 deletions(-)

--- b9dfdd1 ---
b9dfdd1 Updated README.md
 README.md | 62 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++--
 1 file changed, 60 insertions(+), 2 deletions(-)

--- 659d8c1 ---
659d8c1 REFACTOR: Updated the project structure to isolate by modules
 README.md                                           |  4 ++--
 dev-requirements.txt                                | 14 --------------
 infra/environments/dev/main.tf                      |  2 +-
 {projects => modules}/transcribe-module/README.md   | 21 ++++++++++++++++-----
 modules/transcribe-module/dev-requirements.txt      | 14 ++++++++++++++
 modules/transcribe-module/requirements.txt          |  2 ++
 .../transcribe-module/specs/features/1-create-s3.md |  0
 .../specs/features/10-add-segments.md               |  0
 .../specs/features/11-implement-end2end-test.md     |  4 ++--
 .../specs/features/12-integration-test.md           |  0
 .../specs/features/2-create-lambda.md               |  2 +-
 .../transcribe-module/specs/features/4-deploy.md    |  0
 .../specs/features/5-refactor-to-aws-transcribe.md  |  0
 .../specs/features/8-refactor-to-include-video.md   |  0
 .../transcribe-module/specs/features/9-readme.md    |  0
 .../src/handlers/transcribe_handler.py              |  0
 .../src/models/transcription_result.py              |  0
 .../src/services/transcription_service.py           |  0
 .../transcribe-module/src/utils/error_handler.py    |  0
 .../transcribe-module/src/utils/s3_utils.py         |  0
 .../transcribe-module/tests/e2e/README.md           | 10 +++++-----
 .../transcribe-module/tests/e2e/run_e2e_test.sh     |  3 ++-
 .../tests/e2e/test_pipeline_e2e.py                  |  0
 .../test_transcribe_handler_integration.py          |  0
 .../transcribe-module/tests/test_handlers.py        |  0
 .../tests/test_transcription_service.py             |  0
 requirements.txt                                    |  9 ---------
 template.yaml                                       |  2 +-
 28 files changed, 46 insertions(+), 41 deletions(-)

--- 8f4200d ---
8f4200d Added addition unit tests around transcription_service
 .../tests/test_transcription_service.py            | 261 +++++++++++++++++++++
 1 file changed, 261 insertions(+)

--- 253155c ---
253155c REFACTOR: Removed some dead/legacy code paths
 .../src/services/transcription_service.py                  | 14 --------------
 .../transcribe-module/tests/test_transcription_service.py  | 13 -------------
 2 files changed, 27 deletions(-)

--- 2a67bdf ---
2a67bdf Updated the tests to define a rule and integration test
 .cursor/rules/pytest.mdc                           |  73 +++++++
 dev-requirements.txt                               |  14 ++
 .../specs/features/12-integration-test.md          |  20 ++
 .../src/services/transcription_service.py          |  14 ++
 .../test_transcribe_handler_integration.py         | 231 +++++++++++++++++++++
 5 files changed, 352 insertions(+)

```

## Manual Summary

Based on the above logs, summarize the changes into categories:

- **Feature Additions:**
  - (List new features added)

- **Bug Fixes:**
  - (List bugs that were fixed)

- **Refactors:**
  - (List code restructuring or cleaning)

- **Infrastructure Changes:**
  - (List changes to build, CI/CD, etc)

- **Documentation:**
  - (List documentation updates)

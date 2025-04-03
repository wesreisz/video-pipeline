Create an api key and store it in our dev-video-pipeline-secrets. Note dev-video-pipeline-secrets already exists. It is a json file with other secrets in it. Our new key should be called `video-pipeline-api-key` and added to the json file. The key should follow the format "icaet-ak-<random-string>". The total length of the key should be 40 characters.

Fetch the key in initialize_secrets() of the question_handler.py method, retreive and cache the api key from the secret store.

Add the secret only to the question-module. Do not update other modules

Create the secret in terraform. If `video-pipeline-api-key` is not found in the secret manager generate a new one. If one is found, do not overwrite it. Use it.

Every request to the api should include the api key as a header.
Implement a python service class (follow the idioms of the project) that exposes a method to create embeddings using the OpenAI API. It should accept a string as input and return whats recommended by the openai documentation.

Requirements:
* store the api key in a terraform variable that is sent with an environment variable.
* implement an optional minimal integration test using the live api (keep these tests light).
* implement another integration test using a mock of the openai api (keep these tests light).

References:
* https://platform.openai.com/docs/guides/embeddings
* .cursor/rules/project-structure.mdc
* .cursor/rules/python.mdc
* .cursor/rules/pytest.mdc
* .cursor/rules/project-architecture.mdc

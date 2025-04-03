Create a module called question-module that exposes a /query endpoint via API Gateway. It should accept a POST with question and email and validate both. It should log the result and return a simple JSON response. Expose this module with an API Gateway endpoint.

Following the existing project infrastructure guidelines, create a new terraform module calle lambda-question. This should be stored under infra/modules and be configured for dev. The module for the source code should be in modules/question-module

Do not implement unit tests at this point.

You will follow:
* .cursor/rules/project-architecture.mdc
* .cursor/rules/project-structure.mdc
* .cursor/rules/python.mdc
* .cursor/rules/terraform.mdc
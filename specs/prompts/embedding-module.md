Prompt:
Design a basic AWS Lambda function structure in Python that can receive and process a message from SQS. The function should accept an event containing one or more messages and (if several were sent) iterate over each one. The module will be responsible for creating embeddings for each message and storing them into the Pinecone vector database. We will use the OpenAI to create the embeddings. Use the Pinecone quickstart guide (https://docs.pinecone.io/guides/get-started/quickstart) as a reference for integration details.

Context:

The overview of the project is defined in README.md

The project uses Terraform and currently has the following infrastructure defined in infra/environments/dev/main.tf. Attempt to reuse modules as much as possible. For example, you can extend the lambda module rather than creating a new one. 

Update and incorporate the use of Pinecone in the module responsible for storing vector embeddings. Ensure integration with Pinecone's API following their documentation.

Requirements:
* Add this new modules to terraform and make it part of the step function state.
* Add appropriate error handling and logging.
* You should follow the project structure as shown in the role: .cursor/rules/project-structure.mdc.
* Use the existing SQS queue to trigger the embedding-module lambda. Record it with sqs_queue_arn.
* Do not implement the pinecone work yet. Stub it out the logic and provide the terraform variables for "pinecone_api_key".
* Do not implement the openai work yet. Stub it out the logic and provide the terraform variables for "openai_api_key".
* Use Terraform to create the Lambda function following the guidelines in: @.cursor/rules/terraform.mdc.
* Follow Python best practices defined in: .cursor/rules/python.mdc.
* Follow architecture practices in: .cursor/rules/project-structure.mdc.
* Do not implement the pinecone work yet. Stub it out though.


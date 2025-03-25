Prompt:
Design a basic AWS Lambda function structure in Python that can receive and process a message from SQS. The function should accept an event containing one or more messages and (if several were sent) iterate over each one. The module will be responsible for creating embeddings for each message and storing them into the Pinecone vector database. We will use OpenAI to create the embeddings. Use the Pinecone quickstart guide (https://docs.pinecone.io/guides/get-started/quickstart) as a reference for integration details.

Context:
The overview of the project is defined in README.md

The project uses Terraform and currently has the following infrastructure defined in infra/environments/dev/main.tf. Attempt to reuse modules as much as possible. For example, you can extend the lambda module rather than creating a new one. 

The embedding module receives messages from the chunking module in the following format:
* Message contains: chunk_id (5-character unique identifier), text (the content to embed), start_time, and end_time
* The embedding Lambda logs each processed chunk with the format: "Processing chunk CHUNK_ID: TEXT"

Requirements:
* Add this new module to terraform and make it part of the step function state.
* Add appropriate error handling and logging.
* You should follow the project structure as shown in the role: .cursor/rules/project-structure.mdc.
* Use the existing SQS queue to trigger the embedding-module lambda. Record it with sqs_queue_arn.
* Implement logging that matches the format: "Processing chunk CHUNK_ID: TEXT" for each processed message.
* STUB: Do not implement the actual Pinecone integration yet. Provide the terraform variables for "pinecone_api_key" and stub the service interface.
* STUB: Do not implement the actual OpenAI integration yet. Provide the terraform variables for "openai_api_key" and stub the service interface.
* Use Terraform to create the Lambda function following the guidelines in: @.cursor/rules/terraform.mdc.
* Follow Python best practices defined in: .cursor/rules/python.mdc.
* Follow architecture practices in: .cursor/rules/project-structure.mdc.

Implementation Notes:
* The embedding module is triggered by messages from an SQS queue that receives chunks from the chunking module
* Each chunk contains a unique 5-character ID and the text to be embedded
* The module currently stubs the OpenAI embedding creation and Pinecone storage functionality
* End-to-end tests verify the message flow from chunking through to embedding processing
* Logging format is standardized to match the expected test format


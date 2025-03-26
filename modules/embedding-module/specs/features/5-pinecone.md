# Pinecone Vector Database Integration

Implement (or update) the Python service class `pinecone_service.py` that exposes a method to upsert embeddings into the Pinecone managed service. The service should follow the project's idioms and patterns. The service should contain everything needed to handle the upsert and return a successful or error response.

This is an example of what we're looking to create: https://docs.pinecone.io/guides/data/upsert-data

## Data Structure
The upsert operation should include a collection called `talk_metadata` containing:
* `speaker`: Array of speaker names
* `start_time`: the start time of the chunk (segment)
* `end_time`: the start time of the chunk (segment)
* `title`: Talk title
* `track`: Track name
* `day`: Day of the talk
* `text`: The actual text content of the chunk
* `original_file`: Original media file name (optional)
* `segment_id`: Original segment ID from transcription (optional)

(All fields, except start_time and end_time, are strings. start_time and end_time are in the form '28.909' (<MM>.<ss>). All will be passed into the service).

## Technical Requirements
1. **API Key Management**:
   * Store the Pinecone API key in AWS Secret Manager (you should follow the pattern used in `openai_service.py` for access keys)
   * Implement necessary Terraform changes to add `pinecone_api_key`
   * Do not implement test or integration tests at this point

2. **Index Configuration**:
   * Use serverless indexes in AWS us-east-1 region (required for free tier)
   * Configure for OpenAI embedding dimension=1536
   * Use cosine similarity metric
   * Auto-create index if it doesn't exist

3. **Service Implementation**:
   * Follow `OpenAIService` patterns for error handling and logging
   * Implement proper response models using dataclasses
   * Add comprehensive error handling for API failures
   * Include detailed logging for operations and errors
   * Support namespace parameter for vector organization

4. **Lambda Layer Requirements**:
   * Use pinecone==6.0.2 (never use deprecated pinecone-client)
   * Use HTTP client only (never gRPC)
   * Ensure all dependencies are Linux-compatible
   * No transitive dependencies in requirements.txt
   * No MacOS/Darwin libraries in layer
   * Follow existing lambda layer approach for dependencies

## Environment Variables
* `PINECONE_API_KEY`: API key for authentication
* `PINECONE_ENVIRONMENT`: Environment setting (defaults to us-east-1)
* `PINECONE_INDEX_NAME`: Name of the index (defaults to talk-embeddings)

## References
* [Pinecone Upsert Documentation](https://docs.pinecone.io/guides/data/upsert-data)
* Project Rules:
  - .cursor/rules/project-structure.mdc
  - .cursor/rules/python.mdc
  - .cursor/rules/project-architecture.mdc
  - .cursor/rules/terraform.mdc

## Notes
* Free tier is limited to AWS us-east-1 region
* Index creation requires specific configuration for the free tier
* Error handling should follow project standards
* Logging should be implemented for key operations
* Use pinecone==6.0.2. Never use the deprecated library pinecone-client.
* Always use requirements.txt or dev-requirements.txt to install libraries
* Use the HTTP Client and never gRPC: https://docs.pinecone.io/reference/python-sdk
* Leverage the lambda layer approach to embed dependencies, do not use docker
* Do not include transitive dependencies in requirements.txt.
* Use no more than two requirements.txt + dev-requirements.txt files (one for the existing lambda layer and one the existing embedding-module.)
* Follow the patterns used in modules/embedding-module/src/services/openai_service.py as a blueprint
* Never include MacOS or Darwin libraries in requirements.txt. Always use the linux version compatible with AWS Lambda.
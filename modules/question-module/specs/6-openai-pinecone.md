# Question Module Implementation with Lambda Layer Structure

Building on our existing infrastructure (access control, secrets management, and authorization), implement the core question-answering functionality using OpenAI embeddings and Pinecone vector search.

## Project Structure
```
modules/question-module/
├── layer/                      # Lambda layer packaging
│   ├── python/                 # Python packages for layer
│   ├── requirements.txt        # Layer-specific dependencies
│   ├── 1-install.sh           # Script to install dependencies
│   └── 2-package.sh           # Script to create layer ZIP
├── src/                        # Source code
│   ├── handlers/              # Lambda handlers
│   ├── models/                # Data models
│   ├── services/              # Business logic services
│   └── utils/                 # Utility functions
```

## Dependencies and Versions
- OpenAI SDK: Latest version (3.x)
- Pinecone Client: Latest version (3.x)
- Python: 3.11
- Additional required packages:
  - loguru: For structured logging
  - boto3: For AWS services interaction

## Integration Rules
1. API Integration:
   - Use OpenAI's text-embedding-ada-002 model for embeddings
   - Use Pinecone's serverless instance for vector storage
   - Implement proper error handling for both services

2. Request Processing:
   - Validate all incoming requests
   - Check API key in headers
   - Verify email authorization
   - Process one question per request

3. Response Format:
   - Return top 10 matches from Pinecone
   - Include metadata for each match
   - Use standard HTTP status codes
   - Return JSON responses

4. Error Handling:
   - Handle API timeouts
   - Handle rate limits
   - Handle authentication failures
   - Handle invalid inputs

## Technical Constraints
For this initial implementation:
1. Temporarily hardcode OpenAI and Pinecone API keys (will move to secrets manager in next iteration)
2. Skip unit tests for now
3. Use basic error handling
4. Skip performance optimization

## Known Technical Debt
The following items will be addressed in future iterations:
1. Move API keys to consolidated secrets manager
2. Add comprehensive error handling
3. Add unit tests
4. Add proper logging
5. Add rate limiting
6. Add proper documentation

## Success Criteria
1. Lambda successfully processes questions
2. Embeddings are generated correctly
3. Vector search returns relevant results
4. Authorization works as expected
5. Error cases are handled gracefully

## Next Steps
After this implementation:
1. Move credentials to secrets manager
2. Implement comprehensive testing
3. Add proper logging
4. Add input validation
5. Add rate limiting
6. Add proper documentation

Note: This implementation builds on the existing access control, secrets management, and authorization mechanisms already in place. Focus on the core embedding and retrieval functionality while maintaining security measures.

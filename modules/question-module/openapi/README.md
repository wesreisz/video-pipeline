# Question Module API Specification

This directory contains the OpenAPI specification and related documentation for the Question Module API.

## Files

- `openapi.yaml` - Complete OpenAPI 3.0 specification for the Question API
- `chatgpt-integration.md` - Step-by-step guide for integrating with ChatGPT
- `README.md` - This documentation file

## Overview

The Question Module provides a semantic search API for querying transcribed video content from QCon talks and technical presentations. The API uses OpenAI embeddings and Pinecone vector search to find relevant content segments based on natural language questions.

## ChatGPT Integration

This API is specifically designed to be used by ChatGPT and other AI assistants. The OpenAPI schema serves as the function definition for ChatGPT's function calling capability.

**Quick Start**: Follow the [ChatGPT Integration Guide](chatgpt-integration.md) for detailed setup instructions.

### Using with ChatGPT

1. **Upload the OpenAPI schema** to your ChatGPT configuration
2. **Configure the API endpoint** with your actual domain
3. **Set the API key** in your ChatGPT custom GPT settings
4. **Add the schema** as a custom action in your GPT

### Example ChatGPT Function Call

```json
{
  "name": "queryTranscripts",
  "description": "Search through video transcripts for relevant content",
  "parameters": {
    "type": "object",
    "properties": {
      "question": {
        "type": "string",
        "description": "Question about video content"
      },
      "email": {
        "type": "string", 
        "description": "User's email address"
      }
    },
    "required": ["question", "email"]
  }
}
```

## API Authentication

The API uses API key authentication via the `x-api-key` header:

- **Format**: `icaet-ak-{32-character-string}`
- **Location**: HTTP header
- **Header name**: `x-api-key`

### Getting an API Key

API keys are managed through AWS Secrets Manager and generated during deployment. Contact the system administrators to obtain a valid API key.

## Endpoints

### POST /query

Search through video transcripts using semantic search.

**Request Body:**
```json
{
  "question": "What are the best practices for microservices architecture?",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "pinecone_matches": [
    {
      "speaker": ["Martin Fowler"],
      "start_time": "15.5",
      "end_time": "45.2", 
      "title": "Microservices: Decomposing Applications",
      "track": "Architecture",
      "day": "Tuesday",
      "text": "Event-driven architecture is crucial for microservices...",
      "original_file": "fowler-microservices.mp3",
      "segment_id": "seg_001"
    }
  ]
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `speaker` | array | List of speaker names |
| `start_time` | string | Start time in seconds |
| `end_time` | string | End time in seconds |
| `title` | string | Talk title |
| `track` | string | Conference track |
| `day` | string | Conference day |
| `text` | string | Transcribed content (may be empty) |
| `original_file` | string | Original media filename |
| `segment_id` | string | Unique segment identifier |

## Error Handling

The API returns standard HTTP status codes:

- **200** - Success
- **400** - Bad Request (invalid input)
- **401** - Unauthorized (invalid API key or email)
- **500** - Internal Server Error

Error responses include a descriptive message:

```json
{
  "error": "Invalid email format"
}
```

## Rate Limits

- **100 requests per minute** per API key
- **1000 requests per hour** per API key
- Maximum **5 content matches** per query response

## Best Practices

### Query Guidelines

- Use specific, technical questions for better results
- Include speaker names when asking about specific individuals  
- Reference specific technologies, patterns, or concepts
- Avoid overly broad or general questions

### Integration Tips

- Cache responses when appropriate to reduce API calls
- Handle rate limiting with exponential backoff
- Validate email addresses before making requests
- Store API keys securely (never in client-side code)

## Schema Validation

The OpenAPI schema can be validated using standard tools:

```bash
# Using swagger-codegen
swagger-codegen validate -i openapi.yaml

# Using openapi-generator
openapi-generator validate -i openapi.yaml

# Using redoc-cli
redoc-cli validate openapi.yaml
```

## Development Workflow

### Updating the Schema

1. **Modify the API implementation** in `src/handlers/question_handler.py`
2. **Update the OpenAPI schema** in `openapi.yaml` to match
3. **Test the changes** using the validation tools
4. **Update documentation** as needed
5. **Commit both code and schema changes** together

### Schema Maintenance

- Keep the schema in sync with the actual API implementation
- Update examples when response formats change
- Increment the version number for breaking changes
- Document any new error conditions or status codes

### Testing Integration

```bash
# Test API locally using curl
curl -X POST "http://localhost:3000/query" \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key" \
  -d '{"question": "test question", "email": "test@example.com"}'

# Validate responses against schema
npx swagger-tools validate openapi.yaml response.json
```

## Deployment

The OpenAPI schema should be:

1. **Stored in version control** alongside the implementation
2. **Included in deployment packages** for reference
3. **Used for API documentation generation** 
4. **Provided to API consumers** for integration

## Related Documentation

- [Question Module README](../README.md) - Main module documentation
- [Project Architecture](../../../specs/prompts/3-architecture-review.md) - Overall system architecture
- [API Gateway Configuration](../../../infra/modules/question-module/main.tf) - Infrastructure setup 
# Question Module

This module provides a REST API endpoint for querying the video pipeline system. It allows authorized users to ask questions about the processed video/audio content.

## Architecture

The module consists of:
- API Gateway endpoint for handling HTTP requests
- Lambda function for processing queries
- S3-based access control list for authorization
- AWS Secrets Manager for API key management

### Components

1. **API Gateway**
   - Endpoint: `https://<api-id>.execute-api.<region>.amazonaws.com/dev/query`
   - Supports POST method
   - Requires API key authentication

2. **Lambda Function**
   - Name: `dev_question_handler`
   - Runtime: Python 3.11
   - Handles request validation, authorization, and query processing

3. **Access Control**
   - Uses S3 bucket (`dev-access-list`) to store authorized email addresses
   - Access list file: `access.csv`
   - Format: One email address per line

4. **Authentication**
   - API key required in `x-api-key` header
   - Email-based authorization using access list

## API Documentation

The complete API specification is available as an OpenAPI 3.0 schema:

- **OpenAPI Schema**: [openapi/openapi.yaml](openapi/openapi.yaml)
- **API Documentation**: [openapi/README.md](openapi/README.md)

The OpenAPI schema includes:
- Complete endpoint documentation
- Request/response schemas
- Authentication requirements
- Usage examples for ChatGPT integration
- Error handling specifications

For ChatGPT integration and detailed API usage, refer to the [API specification documentation](openapi/README.md).

## Setup

1. **Dependencies**
   ```
   boto3>=1.26.137
   python-json-logger>=2.0.0
   typing-extensions>=4.5.0
   loguru>=0.7.0
   ```

2. **Required AWS Resources**
   - S3 bucket for access list
   - AWS Secrets Manager for API key
   - IAM role with appropriate permissions

3. **Deployment**
   ```bash
   cd infra/environments/dev
   ./deploy.sh
   ```

## Usage

### Making API Requests

To query the system, send a POST request to the API endpoint:

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/query \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR-API-KEY" \
  -d '{"email": "user@example.com", "question": "What is discussed in the video?"}'
```

Example with anonymized values:
```bash
curl -X POST https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/query \
  -H "Content-Type: application/json" \
  -H "x-api-key: icaet-ak-XXXXXXXXXXXXXXXX" \
  -d '{"email": "user@example.com", "question": "What is your name?"}'
```

### Request Format

```json
{
  "email": "user@example.com",
  "question": "What is discussed in the video?"
}
```

### Response Format

Success Response:
```json
{
  "message": "Question received successfully",
  "question": "What is discussed in the video?",
  "email": "user@example.com"
}
```

Error Response:
```json
{
  "error": "Error message here"
}
```

### Common Error Messages

- `"Invalid or missing API key"`: The API key is either missing or incorrect
- `"Email not authorized"`: The provided email is not in the access list
- `"Invalid request format"`: The request body is malformed or missing required fields

## Authorization

1. **API Key Authentication**
   - API key must be provided in the `x-api-key` header
   - Keys are managed in AWS Secrets Manager
   - Key format: `icaet-ak-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

2. **Email Authorization**
   - Emails must be pre-authorized in the access list
   - Access list is stored in S3: `s3://dev-access-list/access.csv`
   - One email per line in the CSV file

## Development

### Local Testing

1. Set up environment variables:
   ```bash
   export AWS_PROFILE=your-profile
   export AWS_REGION=us-east-1
   ```

2. Run unit tests:
   ```bash
   cd modules/question-module
   python -m pytest tests/
   ```

### Adding Authorized Users

1. Update the access list file locally
2. Deploy the updated list:
   ```bash
   cd infra/environments/dev
   ./deploy.sh
   ```

## Security Considerations

1. API keys should never be committed to version control
2. Access list should be regularly reviewed and updated
3. All requests are logged in CloudWatch
4. S3 bucket has public access blocked
5. Lambda function uses least-privilege IAM permissions

## Monitoring and Logging

- CloudWatch Logs group: `/aws/lambda/dev_question_handler`
- Enhanced logging enabled for debugging
- API Gateway access logs available
- CloudWatch metrics for monitoring Lambda performance

## Troubleshooting

1. **API Key Issues**
   - Verify the key format: `icaet-ak-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
   - Check the `x-api-key` header is correctly set
   - Ensure the key is active in Secrets Manager

2. **Authorization Failures**
   - Verify email is in the access list
   - Check S3 bucket permissions
   - Review Lambda execution role permissions

3. **Lambda Errors**
   - Check CloudWatch Logs for detailed error messages
   - Verify Lambda timeout and memory settings
   - Review Lambda execution role permissions 
# Embedding Module

## Secrets Management

This module uses AWS Secrets Manager to securely store sensitive configuration values. The following secrets are managed:

- OpenAI API Key
- OpenAI Organization ID
- OpenAI Base URL

### Local Development

For local development, you need to set the following environment variables:

```bash
# Required for Terraform deployment
export TF_VAR_openai_api_key="your-openai-api-key"

# Required for local testing
export ENVIRONMENT="dev"  # or "prod" for production
```

### Terraform Deployment

To deploy the secrets:

1. Set the required environment variables (see above)
2. Navigate to the environment directory:
   ```bash
   cd infra/environments/dev
   ```
3. Initialize and apply Terraform:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

### Security Notes

- Never commit sensitive values to the repository
- Always use environment variables with `TF_VAR_` prefix for sensitive Terraform variables
- The secrets are encrypted using AWS KMS
- Access to secrets is controlled via IAM policies
- Secrets are environment-specific (dev/prod)

### Using Secrets in Code

The `SecretsService` class handles all interaction with AWS Secrets Manager:

```python
from services.secrets_service import SecretsService

secrets = SecretsService()
openai_api_key = secrets.get_openai_api_key()
```

### Adding New Secrets

To add a new secret:

1. Add it to the secret string in `infra/modules/secrets/main.tf`
2. Add a getter method in `src/services/secrets_service.py`
3. Update this documentation

### Running Tests

The project includes both unit tests with mocked dependencies and integration tests that use real API calls.

#### Running Unit Tests

To run unit tests (which use mocked dependencies):

```bash
python -m pytest tests/services/test_openai_service.py -v
```

#### Running Integration Tests

Integration tests are skipped by default to avoid unnecessary API calls. To run them:

```bash
# Set required environment variables
export ENVIRONMENT="dev"
export RUN_LIVE_TESTS=1

# Run integration tests
python -m pytest tests/integration/test_openai_service_integration.py -v
```

Note: Integration tests require valid AWS credentials and secrets to be configured. 
# Secret Store Implementation

## Overview
Remove sensitive secrets and variables from the code and store them in AWS Secrets Manager. The implementation should support both local development (using environment variables) and both cloud environments (dev and prod) (using AWS Secrets Manager). Prod is not yet implemented so ignore it for now.

## Current Structure Analysis
The codebase currently uses environment variables for sensitive data:
- OpenAI API configuration in `openai_service.py`
- Pinecone API configuration `pinecone_service.py` (not yet implemented)
- Environment-specific configurations

## Requirements

### Secret Storage
1. **Required Secrets:**
   - `openai_api_key`: OpenAI API key (MUST be set via TF_VAR_openai_api_key environment variable)
   - `pinecone_api_key`: Pinecone database API key (MUST be set via TF_VAR_pinecone_api_key environment variable)
   - `openai_org_id`: Organization ID (set to "org-IQCAET")
   - `openai_base_url`: API endpoint (set to "https://api.openai.com/v1")

2. **Environment Variables:**
   - Test environment should use mock values
   - Production should use AWS Secrets Manager
   - NO local development support needed

### Secret Provisioning
1. **Terraform Resources:**
   ```hcl
   # IMPORTANT: Never hardcode sensitive values here
   # Use environment variables with TF_VAR_ prefix
   
   variable "openai_api_key" {
     description = "OpenAI API Key"
     type        = string
     sensitive   = true
   }

   variable "pinecone_api_key" {
     description = "Pinecone API Key"
     type        = string
     sensitive   = true
   }

   resource "aws_secretsmanager_secret" "embedding_module" {
     name = "${var.environment}-embedding-module-secrets"
     description = "Secrets for the embedding module"
   }

   resource "aws_secretsmanager_secret_version" "embedding_module" {
     secret_id = aws_secretsmanager_secret.embedding_module.id
     secret_string = jsonencode({
       openai_api_key    = var.openai_api_key
       pinecone_api_key  = var.pinecone_api_key
       openai_org_id     = "org-IQCAET"
       openai_base_url   = "https://api.openai.com/v1"
     })
   }
   ```

### Secret Retrieval
1. **Local Development:**
   - Use environment variables:
     ```bash
     OPENAI_API_KEY=sk-your-key-here
     PINECONE_API_KEY=your-pinecone-key
     ```

2. **Production:**
   - Use AWS Secrets Manager with proper IAM roles
   - Implement caching to reduce API calls
   - Handle error cases appropriately

3. **Testing:**
   - Use mock values in test environment
   - Support integration tests with real API keys when needed

### Security Requirements
1. **Environment Variables:**
   - MUST use `TF_VAR_` prefix for all sensitive Terraform variables
   - NEVER commit actual values to the repository
   - Keep sensitive values out of logs
   - Add to .gitignore:
     ```
     *.tfvars
     *.tfvars.json
     .env
     ```

2. **AWS Configuration:**
   - Use KMS encryption for secrets
   - Implement least privilege access
   - Enable secret rotation if needed

3. **Code Standards:**
   - Follow project's Terraform standards
   - Implement proper error handling
   - Add comprehensive logging
   - Document all configuration options
   - NEVER include example values in documentation that could be mistaken for real credentials

## Implementation Steps
1. Create AWS Secrets Manager resources
2. Update Python services to use secrets
3. Implement local development support
4. Update tests and documentation
5. Verify security compliance

## Usage Examples

### Terraform Deployment
```bash
# REQUIRED: Set environment variables before running Terraform
export TF_VAR_openai_api_key="sk-your-key-here"
export TF_VAR_pinecone_api_key="your-pinecone-key"

# Apply changes
terraform plan
terraform apply
```

### Local Development
1. Create `.env` file (add to .gitignore)
2. Set required environment variables
3. Run application

### Testing
```bash
# Run with mock values
python -m pytest

# Run with real API (if needed)
export OPENAI_API_KEY="sk-your-key-here"
export RUN_LIVE_TESTS=1
python -m pytest
```

Output:

Please generate:
Suggest all things that should be stored in teh secret store in the code base (for example, the openai api key and the pinecone database  api should be stored there. Are there any others)

Updated Terraform code examples for:

Creating the secret in AWS Secrets Manager.

Retrieving and decoding the secret in Terraform.

use the reference to get the open api key from the secret store

Explanatory comments and documentation for each code snippet.

Follow all project standards:
* .cursor/rules/project-architecture.mdc
* .cursor/rules/project-structure.mdc
* .cursor/rules/python.mdc
* .cursor/rules/terraform.mdc


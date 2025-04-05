# Development Environment Setup

## Configuration Setup

1. Copy the example terraform variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Update `terraform.tfvars` with your API keys:
   - Replace `your-openai-api-key-here` with your OpenAI API key
   - Replace `your-pinecone-api-key-here` with your Pinecone API key
   - Optionally modify other variables as needed

**Note:** The `terraform.tfvars` file contains sensitive information and is ignored by git. Never commit this file to version control.

## Delete the Infra
To destroy the infra, run terraform destroy. The secret store will not automatically
delete for a few days (for safety). This command forces the deletion:
`aws secretsmanager delete-secret --secret-id dev-video-pipeline-secrets --force-delete-without-recovery`

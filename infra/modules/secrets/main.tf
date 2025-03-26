variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

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

variable "log_level" {
  description = "Log level for the application"
  type        = string
  default     = "INFO"
}

variable "sqs_queue_url" {
  description = "URL of the SQS queue"
  type        = string
}

# KMS key for encrypting the secrets
resource "aws_kms_key" "secrets" {
  description             = "KMS key for embedding module secrets"
  deletion_window_in_days = 7
  enable_key_rotation    = true

  tags = {
    Environment = var.environment
    Service     = "embedding-module"
  }
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.environment}-embedding-module-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# Secrets Manager secret
resource "aws_secretsmanager_secret" "embedding_module" {
  name        = "${var.environment}-embedding-module-secrets"
  description = "Secrets for the embedding module"
  kms_key_id  = aws_kms_key.secrets.arn

  tags = {
    Environment = var.environment
    Service     = "embedding-module"
  }
}

resource "aws_secretsmanager_secret_version" "embedding_module" {
  secret_id = aws_secretsmanager_secret.embedding_module.id
  secret_string = jsonencode({
    openai_api_key    = var.openai_api_key
    pinecone_api_key  = var.pinecone_api_key
    openai_org_id     = "org-b6y2SlhOMQnynny57KMpe8Bk"
    openai_base_url   = "https://api.openai.com/v1"
    log_level         = var.log_level
    sqs_queue_url     = var.sqs_queue_url
    openai_timeout    = "20.0"
    openai_max_retries = "3"
  })
}

# IAM policy for accessing the secrets
data "aws_iam_policy_document" "secrets_access" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [aws_secretsmanager_secret.embedding_module.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources = [aws_kms_key.secrets.arn]
  }
}

resource "aws_iam_policy" "secrets_access" {
  name        = "${var.environment}-embedding-module-secrets-access"
  description = "Policy for accessing embedding module secrets"
  policy      = data.aws_iam_policy_document.secrets_access.json
}

output "secret_arn" {
  description = "ARN of the created secret"
  value       = aws_secretsmanager_secret.embedding_module.arn
}

output "secret_name" {
  description = "Name of the created secret"
  value       = aws_secretsmanager_secret.embedding_module.name
}

output "secrets_access_policy_arn" {
  description = "ARN of the IAM policy for accessing secrets"
  value       = aws_iam_policy.secrets_access.arn
} 
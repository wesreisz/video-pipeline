# KMS key for encrypting the secrets
resource "aws_kms_key" "secrets" {
  description             = "KMS key for application secrets"
  deletion_window_in_days = 7
  enable_key_rotation    = true

  tags = {
    Environment = var.environment
    Service     = "video-pipeline"
  }
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.environment}-video-pipeline-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# Secrets Manager secret
resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.environment}-video-pipeline-secrets"
  description = "Secrets for the video pipeline application"
  kms_key_id  = aws_kms_key.secrets.arn

  tags = {
    Environment = var.environment
    Service     = "video-pipeline"
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    openai_api_key     = var.openai_api_key
    pinecone_api_key   = var.pinecone_api_key
    openai_org_id      = "org-b6y2SlhOMQnynny57KMpe8Bk"
    openai_base_url    = "https://api.openai.com/v1"
    log_level          = var.log_level
    sqs_queue_url      = var.sqs_queue_url
    openai_timeout     = "20.0"
    openai_max_retries = "3"
    access_list_url    = "https://dev-access-list.s3.us-east-1.amazonaws.com/access.csv"
    video-pipeline-api-key = coalesce(var.video_pipeline_api_key, "icaet-ak-${random_string.api_key_suffix.result}")
  })
}

# Generate random string for API key if not provided
resource "random_string" "api_key_suffix" {
  length  = 32  # 32 chars + "icaet-ak-" prefix = 40 chars total
  special = false
  upper   = true
  lower   = true
  numeric = true
}

# IAM policy for accessing the secrets
data "aws_iam_policy_document" "secrets_access" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [aws_secretsmanager_secret.app_secrets.arn]
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
  name        = "${var.environment}-video-pipeline-secrets-access"
  description = "Policy for accessing video pipeline secrets"
  policy      = data.aws_iam_policy_document.secrets_access.json
}

output "secret_arn" {
  description = "ARN of the created secret"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "secret_name" {
  description = "Name of the created secret"
  value       = aws_secretsmanager_secret.app_secrets.name
}

output "secrets_access_policy_arn" {
  description = "ARN of the IAM policy for accessing secrets"
  value       = aws_iam_policy.secrets_access.arn
} 
# Lambda Function Module

# Create archive of source code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = var.output_path
}

# Lambda IAM Role
resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Lambda basic execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# S3 access policy if needed
resource "aws_iam_policy" "s3_access" {
  count = length(var.s3_bucket_arns) > 0 ? 1 : 0
  
  name        = "${var.function_name}_s3_access"
  description = "S3 access for ${var.function_name} Lambda"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = concat(
          var.s3_bucket_arns,
          [for arn in var.s3_bucket_arns : "${arn}/*"]
        )
      }
    ]
  })
}

# Secrets Manager access policy
resource "aws_iam_policy" "secrets_access" {
  name        = "${var.function_name}_secrets_access"
  description = "Secrets Manager access for ${var.function_name} Lambda"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Effect   = "Allow"
        Resource = ["arn:aws:secretsmanager:*:*:secret:dev-video-pipeline-secrets-*"]
      }
    ]
  })
}

# AWS Transcribe access policy
resource "aws_iam_policy" "transcribe_access" {
  count = var.enable_transcribe ? 1 : 0
  
  name        = "${var.function_name}_transcribe_access"
  description = "AWS Transcribe access for ${var.function_name} Lambda"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob",
          "transcribe:ListTranscriptionJobs"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "transcribe_access" {
  count = var.enable_transcribe ? 1 : 0
  
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.transcribe_access[0].arn
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  count = length(var.s3_bucket_arns) > 0 ? 1 : 0
  
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.s3_access[0].arn
}

resource "aws_iam_role_policy_attachment" "secrets_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.secrets_access.arn
}

# Lambda function
resource "aws_lambda_function" "lambda" {
  function_name    = var.function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = var.handler
  runtime          = var.runtime
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = var.timeout
  memory_size      = var.memory_size
  
  # Use the layers variable
  layers = var.layers
  
  environment {
    variables = var.environment_variables
  }
  
  tags = var.tags
} 
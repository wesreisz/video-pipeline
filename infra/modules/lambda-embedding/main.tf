locals {
  module_name = "lambda-embedding"
}

# Lambda layer for dependencies
resource "aws_lambda_layer_version" "dependencies" {
  filename            = "${path.module}/../../../modules/embedding-module/layer/layer_content.zip"
  layer_name          = "${var.environment}_${local.module_name}_dependencies"
  compatible_runtimes = ["python3.11"]
  description        = "Dependencies for ${var.environment} embedding Lambda function"
  source_code_hash   = filebase64sha256("${path.module}/../../../modules/embedding-module/layer/layer_content.zip")
}

# Lambda function for embeddings
module "lambda" {
  source = "../lambda"
  
  function_name = "${var.environment}_media_embedding"
  handler       = "handlers/embedding_handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512
  
  source_dir  = "../../../modules/embedding-module/src"
  output_path = "../../build/embedding_lambda.zip"
  
  environment_variables = {
    ENVIRONMENT = var.environment
    USE_ENV_FALLBACK = "false"
  }
  
  # Add the layer to the Lambda function
  layers = [aws_lambda_layer_version.dependencies.arn]
  
  tags = merge(var.tags, {
    Module = local.module_name
  })
}

# IAM role policy for SQS access
resource "aws_iam_policy" "sqs_policy" {
  name        = "${var.environment}_${local.module_name}_sqs_policy"
  description = "Allow Lambda to receive messages from SQS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [var.sqs_queue_arn]
      }
    ]
  })
}

# Attach SQS policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_sqs" {
  role       = module.lambda.role_name
  policy_arn = aws_iam_policy.sqs_policy.arn
}

# Attach Secrets Manager access policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_secrets" {
  role       = module.lambda.role_name
  policy_arn = var.secrets_access_policy_arn
}

# Lambda SQS trigger
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = var.sqs_queue_arn
  function_name    = module.lambda.function_name
  batch_size       = var.sqs_batch_size
  enabled          = true
  
  scaling_config {
    maximum_concurrency = var.max_concurrency
  }
} 
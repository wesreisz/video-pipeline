locals {
  module_name = "lambda-embedding"
}

# Lambda function for embeddings
module "lambda" {
  source = "../lambda"
  
  function_name = "${var.environment}_media_embedding"
  handler       = "handlers/embedding_handler.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 512
  
  source_dir  = "../../../modules/embedding-module/src"
  output_path = "../../build/embedding_lambda.zip"
  
  environment_variables = {
    OPENAI_API_KEY   = var.openai_api_key
    PINECONE_API_KEY = var.pinecone_api_key
    LOG_LEVEL        = var.log_level
    SQS_QUEUE_URL    = var.sqs_queue_url
  }
  
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

# Lambda SQS trigger
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = var.sqs_queue_arn
  function_name    = module.lambda.function_name
  batch_size       = var.sqs_batch_size
  enabled          = true
} 
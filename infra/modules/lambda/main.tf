# Lambda Function Module

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "handler" {
  description = "Handler function for Lambda"
  type        = string
}

variable "runtime" {
  description = "Runtime for Lambda function"
  type        = string
  default     = "python3.9"
}

variable "timeout" {
  description = "Timeout in seconds"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Memory size in MB"
  type        = number
  default     = 128
}

variable "source_dir" {
  description = "Directory of source code to be zipped"
  type        = string
}

variable "output_path" {
  description = "Path where the zip file will be created"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables for Lambda function"
  type        = map(string)
  default     = {}
}

variable "s3_bucket_arns" {
  description = "List of S3 bucket ARNs the Lambda needs access to"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

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

resource "aws_iam_role_policy_attachment" "s3_access" {
  count = length(var.s3_bucket_arns) > 0 ? 1 : 0
  
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.s3_access[0].arn
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
  
  environment {
    variables = var.environment_variables
  }
  
  tags = var.tags
}

# Outputs
output "function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.lambda.function_name
}

output "function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.lambda.arn
}

output "role_arn" {
  description = "ARN of the IAM role"
  value       = aws_iam_role.lambda_role.arn
} 
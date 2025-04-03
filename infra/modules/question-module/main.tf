locals {
  module_name = "question-module"
}

# Lambda layer for dependencies
resource "aws_lambda_layer_version" "dependencies" {
  filename            = "${path.module}/../../../modules/question-module/layer/layer_content.zip"
  layer_name          = "${var.environment}_${local.module_name}_dependencies"
  compatible_runtimes = ["python3.11"]
  description        = "Dependencies for ${var.environment} question Lambda function"
  source_code_hash   = filebase64sha256("${path.module}/../../../modules/question-module/layer/layer_content.zip")
}

# Lambda function
module "lambda" {
  source = "../lambda"
  
  function_name = "${var.environment}_question_handler"
  handler       = "handlers/question_handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512
  
  source_dir  = "../../../modules/question-module/src"
  output_path = "../../build/question_lambda.zip"
  
  environment_variables = {
    ENVIRONMENT = var.environment
    LOG_LEVEL  = var.log_level
  }
  
  layers = [aws_lambda_layer_version.dependencies.arn]
  
  tags = merge(var.tags, {
    Module = local.module_name
  })
}

# S3 access policy for access list
resource "aws_iam_policy" "s3_access" {
  name        = "${var.environment}_question_s3_access"
  description = "S3 access for question Lambda"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = [
          "arn:aws:s3:::dev-access-list/*"
        ]
      }
    ]
  })
}

# Attach S3 access policy to Lambda role
resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = module.lambda.role_name
  policy_arn = aws_iam_policy.s3_access.arn
}

# Attach Secrets Manager access policy to Lambda role
resource "aws_iam_role_policy_attachment" "secrets_access" {
  role       = module.lambda.role_name
  policy_arn = var.secrets_access_policy_arn
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "question_api" {
  name        = "${var.environment}_question_api"
  description = "API Gateway for question module"

  tags = merge(var.tags, {
    Module = local.module_name
  })
}

# API Gateway resource for /query endpoint
resource "aws_api_gateway_resource" "query" {
  rest_api_id = aws_api_gateway_rest_api.question_api.id
  parent_id   = aws_api_gateway_rest_api.question_api.root_resource_id
  path_part   = "query"
}

# API Gateway POST method
resource "aws_api_gateway_method" "query_post" {
  rest_api_id   = aws_api_gateway_rest_api.question_api.id
  resource_id   = aws_api_gateway_resource.query.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway integration with Lambda
resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.question_api.id
  resource_id = aws_api_gateway_resource.query.id
  http_method = aws_api_gateway_method.query_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = module.lambda.invoke_arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.question_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "question_api" {
  rest_api_id = aws_api_gateway_rest_api.question_api.id

  depends_on = [
    aws_api_gateway_integration.lambda
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway stage
resource "aws_api_gateway_stage" "question_api" {
  deployment_id = aws_api_gateway_deployment.question_api.id
  rest_api_id   = aws_api_gateway_rest_api.question_api.id
  stage_name    = var.environment
}

output "function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda.function_name
}

output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_stage.question_api.invoke_url}/query"
} 
# AWS Lambda Terraform Module

This module provisions an AWS Lambda function along with the necessary IAM roles and permissions.

## Features

- Creates Lambda function from source code directory
- Configures basic Lambda execution role
- Optional S3 bucket access permissions
- Configurable runtime, memory size, and timeout

## Usage

```hcl
module "lambda_function" {
  source = "../modules/lambda"

  function_name = "my-lambda-function"
  handler       = "main.handler"
  runtime       = "python3.9"
  source_dir    = "${path.module}/lambda_code"
  output_path   = "${path.module}/lambda_function.zip"
  
  timeout     = 60
  memory_size = 256
  
  environment_variables = {
    ENV_VAR1 = "value1"
    ENV_VAR2 = "value2"
  }
  
  s3_bucket_arns = [
    "arn:aws:s3:::my-bucket",
  ]
  
  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| function_name | Name of the Lambda function | string | n/a | yes |
| handler | Handler function for Lambda | string | n/a | yes |
| runtime | Runtime for Lambda function | string | "python3.9" | no |
| timeout | Timeout in seconds | number | 30 | no |
| memory_size | Memory size in MB | number | 128 | no |
| source_dir | Directory of source code to be zipped | string | n/a | yes |
| output_path | Path where the zip file will be created | string | n/a | yes |
| environment_variables | Environment variables for Lambda function | map(string) | {} | no |
| s3_bucket_arns | List of S3 bucket ARNs the Lambda needs access to | list(string) | [] | no |
| tags | Tags to apply to resources | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| function_name | Name of the Lambda function |
| function_arn | ARN of the Lambda function |
| role_arn | ARN of the IAM role | 
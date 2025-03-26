# Lambda Embedding Module

This module creates the infrastructure for the embedding Lambda function, which is responsible for generating embeddings for text chunks using OpenAI.

## Features

- Lambda function for processing text chunks and generating embeddings
- SQS trigger for processing messages in batches
- IAM roles and policies for secure access
- Integration with OpenAI service

## Usage

```hcl
module "lambda_embedding" {
  source = "../../modules/lambda-embedding"

  environment      = "dev"
  openai_api_key   = var.openai_api_key
  sqs_queue_url    = module.audio_segments_queue.queue_url
  sqs_queue_arn    = module.audio_segments_queue.queue_arn
  
  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 5.91.0 |
| aws | >= 5.0.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| environment | Environment name (e.g., dev, prod) | `string` | n/a | yes |
| openai_api_key | API key for OpenAI service | `string` | n/a | yes |
| log_level | Log level for Lambda function | `string` | `"INFO"` | no |
| sqs_queue_url | URL of the SQS queue to process | `string` | n/a | yes |
| sqs_queue_arn | ARN of the SQS queue to process | `string` | n/a | yes |
| sqs_batch_size | Number of records to process in each batch | `number` | `10` | no |
| tags | A map of tags to add to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| function_name | Name of the Lambda function |
| function_arn | ARN of the Lambda function |
| role_name | Name of the Lambda IAM role |
| role_arn | ARN of the Lambda IAM role |

## Security Considerations

- API keys are marked as sensitive and should be stored securely
- IAM roles follow least privilege principle
- SQS access is restricted to necessary actions only 
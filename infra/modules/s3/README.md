# S3 Bucket Module

This module creates an S3 bucket with optional versioning and default encryption enabled.

## Features

- Creates an S3 bucket with customizable name
- Configurable versioning
- Server-side encryption enabled by default with AES256
- Public access blocked by default for security

## Usage

```terraform
module "s3_bucket" {
  source = "../../modules/s3"

  bucket_name       = "my-example-bucket"
  enable_versioning = true
  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| bucket_name | Name of the S3 bucket | string | - | yes |
| tags | A map of tags to assign to the bucket | map(string) | {} | no |
| enable_versioning | Enable versioning for the S3 bucket | bool | false | no |

## Outputs

| Name | Description |
|------|-------------|
| bucket_id | The name of the bucket |
| bucket_arn | The ARN of the bucket |
| bucket_domain_name | The bucket domain name | 
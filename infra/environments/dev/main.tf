terraform {
  backend "s3" {
    bucket         = "video-pipeline-terraform-state"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "video-pipeline-terraform-locks-dev"
    encrypt        = true
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Environment = "dev"
      Project     = "video-pipeline"
      ManagedBy   = "terraform"
    }
  }
}

# S3 buckets for media files (audio and video) and transcriptions
module "media_bucket" {
  source = "../../modules/s3"
  
  bucket_name = "dev-media-transcribe-input"
  tags = {
    Environment = "dev"
    Project     = "transcribe-module"
  }
}

module "transcription_bucket" {
  source = "../../modules/s3"
  
  bucket_name = "dev-media-transcribe-output"
  tags = {
    Environment = "dev"
    Project     = "transcribe-module"
  }
}

# Chunking output bucket
module "chunking_bucket" {
  source = "../../modules/s3"
  
  bucket_name = "dev-media-chunking-output"
  tags = {
    Environment = "dev"
    Project     = "chunking-module"
  }
}

# Lambda function for transcription
module "transcribe_lambda" {
  source = "../../modules/lambda"
  
  function_name = "dev_media_transcribe"
  handler       = "handlers/transcribe_handler.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 256
  
  source_dir  = "../../../modules/transcribe-module/src"
  output_path = "../../build/transcribe_lambda.zip"
  
  environment_variables = {
    TRANSCRIPTION_OUTPUT_BUCKET = module.transcription_bucket.bucket_id
    TRANSCRIBE_REGION           = "us-east-1"
  }
  
  s3_bucket_arns = [
    module.media_bucket.bucket_arn,
    module.transcription_bucket.bucket_arn
  ]
  
  enable_transcribe = true
  
  tags = {
    Environment = "dev"
    Project     = "transcribe-module"
  }
}

# Lambda function for chunking
module "chunking_lambda" {
  source = "../../modules/lambda"
  
  function_name = "dev_media_chunking"
  handler       = "handlers/chunking_handler.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 256
  
  source_dir  = "../../../modules/chunking-module/src"
  output_path = "../../build/chunking_lambda.zip"
  
  environment_variables = {
    CHUNKING_OUTPUT_BUCKET = module.chunking_bucket.bucket_id
  }
  
  s3_bucket_arns = [
    module.transcription_bucket.bucket_arn,
    module.chunking_bucket.bucket_arn
  ]
  
  tags = {
    Environment = "dev"
    Project     = "chunking-module"
  }
}

# S3 Event triggers for Lambda - Both Audio and Video Files
resource "aws_s3_bucket_notification" "media_notification" {
  bucket = module.media_bucket.bucket_id
  
  # Audio formats
  lambda_function {
    lambda_function_arn = module.transcribe_lambda.function_arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".mp3"
    id                  = "audio-mp3-notification"
  }

  lambda_function {
    lambda_function_arn = module.transcribe_lambda.function_arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".wav"
    id                  = "audio-wav-notification"
  }
  
  # Video formats
  lambda_function {
    lambda_function_arn = module.transcribe_lambda.function_arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".mp4"
    id                  = "video-mp4-notification"
  }

  lambda_function {
    lambda_function_arn = module.transcribe_lambda.function_arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".webm"
    id                  = "video-webm-notification"
  }
  
  # Make sure the Lambda permission is created before the notification
  depends_on = [aws_lambda_permission.allow_bucket]
}

# S3 Event triggers for Chunking Lambda - Triggered by new transcription files
resource "aws_s3_bucket_notification" "transcription_notification" {
  bucket = module.transcription_bucket.bucket_id
  
  lambda_function {
    lambda_function_arn = module.chunking_lambda.function_arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".json"
    id                  = "transcription-json-notification"
  }
  
  # Make sure the Lambda permission is created before the notification
  depends_on = [aws_lambda_permission.allow_transcription_bucket]
}

# Lambda permission for S3 to invoke transcribe lambda
resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = module.transcribe_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.media_bucket.bucket_arn
}

# Lambda permission for S3 to invoke chunking lambda
resource "aws_lambda_permission" "allow_transcription_bucket" {
  statement_id  = "AllowExecutionFromTranscriptionBucket"
  action        = "lambda:InvokeFunction"
  function_name = module.chunking_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.transcription_bucket.bucket_arn
}

# Outputs
output "media_bucket_name" {
  value = module.media_bucket.bucket_id
}

output "transcription_bucket_name" {
  value = module.transcription_bucket.bucket_id
}

output "chunking_bucket_name" {
  value = module.chunking_bucket.bucket_id
}

output "transcribe_lambda_function_name" {
  value = module.transcribe_lambda.function_name
}

output "chunking_lambda_function_name" {
  value = module.chunking_lambda.function_name
} 
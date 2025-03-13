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

# S3 bucket for storing video files
module "video_storage_bucket" {
  source = "../../modules/s3"

  bucket_name       = "${var.project_name}-video-storage-${var.environment}"
  enable_versioning = true
  tags = {
    Description = "Storage for video files that need to be processed"
    Service     = "Video Storage"
  }
}

# S3 buckets for audio files and transcriptions
module "audio_bucket" {
  source = "../../modules/s3"
  
  bucket_name = "dev-audio-transcribe-input"
  tags = {
    Environment = "dev"
    Project     = "transcribe-module"
  }
}

module "transcription_bucket" {
  source = "../../modules/s3"
  
  bucket_name = "dev-audio-transcribe-output"
  tags = {
    Environment = "dev"
    Project     = "transcribe-module"
  }
}

# Lambda function for transcription
module "transcribe_lambda" {
  source = "../../modules/lambda"
  
  function_name = "dev_audio_transcribe"
  handler       = "handlers/transcribe_handler.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 256
  
  source_dir  = "../../../projects/transcribe-module/src"
  output_path = "../../build/transcribe_lambda.zip"
  
  environment_variables = {
    TRANSCRIPTION_OUTPUT_BUCKET = module.transcription_bucket.bucket_id
    TRANSCRIBE_REGION           = "us-east-1"
  }
  
  s3_bucket_arns = [
    module.audio_bucket.bucket_arn,
    module.transcription_bucket.bucket_arn
  ]
  
  enable_transcribe = true
  
  tags = {
    Environment = "dev"
    Project     = "transcribe-module"
  }
}

# S3 Event trigger for Lambda
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = module.audio_bucket.bucket_id
  
  lambda_function {
    lambda_function_arn = module.transcribe_lambda.function_arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".mp3"
  }
  
  # Make sure the Lambda permission is created before the notification
  depends_on = [aws_lambda_permission.allow_bucket]
}

# Lambda permission for S3 to invoke
resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = module.transcribe_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.audio_bucket.bucket_arn
}

# Outputs
output "audio_bucket_name" {
  value = module.audio_bucket.bucket_id
}

output "transcription_bucket_name" {
  value = module.transcription_bucket.bucket_id
}

output "lambda_function_name" {
  value = module.transcribe_lambda.function_name
} 
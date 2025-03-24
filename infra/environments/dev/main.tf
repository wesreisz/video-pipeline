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

# Lambda function for transcription
module "transcribe_lambda" {
  source = "../../modules/lambda"
  
  function_name = "dev_media_transcribe"
  handler       = "handlers/transcribe_handler.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
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
    TRANSCRIPTION_BUCKET = module.transcription_bucket.bucket_id
    SQS_QUEUE_URL       = module.audio_segments_queue.queue_url
  }
  
  s3_bucket_arns = [
    module.transcription_bucket.bucket_arn
  ]
  
  tags = {
    Environment = "dev"
    Project     = "chunking-module"
  }
}

# Lambda function for embeddings
module "lambda_embedding" {
  source = "../../modules/lambda-embedding"
  
  environment      = var.environment
  openai_api_key   = var.openai_api_key
  pinecone_api_key = var.pinecone_api_key
  sqs_queue_url    = module.audio_segments_queue.queue_url
  sqs_queue_arn    = module.audio_segments_queue.queue_arn
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# EventBridge Role for S3 events
resource "aws_iam_role" "eventbridge_role" {
  name = "dev_eventbridge_s3_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}

# EventBridge permissions to invoke Step Functions
resource "aws_iam_policy" "eventbridge_sfn_policy" {
  name        = "dev_eventbridge_sfn_policy"
  description = "Allow EventBridge to start Step Functions execution"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "states:StartExecution"
        Resource = aws_sfn_state_machine.video_processing.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eventbridge_sfn_attach" {
  role       = aws_iam_role.eventbridge_role.name
  policy_arn = aws_iam_policy.eventbridge_sfn_policy.arn
}

# Step Functions IAM Role
resource "aws_iam_role" "step_functions_role" {
  name = "dev_step_functions_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}

# Step Functions Lambda Invoke Permission
resource "aws_iam_policy" "sfn_lambda_policy" {
  name        = "dev_sfn_lambda_policy"
  description = "Allow Step Functions to invoke Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "lambda:InvokeFunction"
        Resource = [
          module.transcribe_lambda.function_arn,
          module.chunking_lambda.function_arn,
          module.lambda_embedding.function_arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sfn_lambda_attach" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = aws_iam_policy.sfn_lambda_policy.arn
}

# Step Functions State Machine
resource "aws_sfn_state_machine" "video_processing" {
  name     = "dev_video_processing"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = jsonencode({
    Comment = "Video processing pipeline with transcribe, chunking, and embedding"
    StartAt = "PrepareS3EventData"
    States = {
      PrepareS3EventData = {
        Type = "Pass"
        Parameters = {
          "bucket.$" = "$.detail.requestParameters.bucketName"
          "key.$" = "$.detail.requestParameters.key"
        }
        ResultPath = "$.s3event"
        Next = "TranscribeMedia"
      }
      TranscribeMedia = {
        Type = "Task"
        Resource = module.transcribe_lambda.function_arn
        Parameters = {
          "detail": {
            "requestParameters": {
              "bucketName.$": "$.s3event.bucket",
              "key.$": "$.s3event.key"
            }
          }
        }
        ResultPath = "$.transcribeResult"
        Next = "TranscribeSucceeded?"
        Retry = [
          {
            ErrorEquals = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts = 5
            BackoffRate = 2.0
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath = "$.error"
            Next = "TranscribeFailed"
          }
        ]
      }
      "TranscribeSucceeded?" = {
        Type = "Choice"
        Choices = [
          {
            Variable = "$.transcribeResult.statusCode"
            NumericEquals = 200
            Next = "WaitForTranscriptionCompletion"
          }
        ]
        Default = "TranscribeFailed"
      }
      WaitForTranscriptionCompletion = {
        Type = "Wait"
        Seconds = 60
        Next = "ChunkTranscription"
      }
      ChunkTranscription = {
        Type = "Task"
        Resource = module.chunking_lambda.function_arn
        Parameters = {
          "detail.$": "$.transcribeResult.detail"
        }
        ResultPath = "$.chunkResult"
        Next = "ChunkSucceeded?"
        Retry = [
          {
            ErrorEquals = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts = 3
            BackoffRate = 2.0
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath = "$.error"
            Next = "ChunkingFailed"
          }
        ]
      }
      "ChunkSucceeded?" = {
        Type = "Choice"
        Choices = [
          {
            Variable = "$.chunkResult.statusCode"
            NumericEquals = 200
            Next = "CreateEmbeddings"
          }
        ]
        Default = "ChunkingFailed"
      }
      CreateEmbeddings = {
        Type = "Task"
        Resource = module.lambda_embedding.function_arn
        Parameters = {
          "detail.$": "$.chunkResult.detail"
        }
        ResultPath = "$.embeddingResult"
        Next = "EmbeddingSucceeded?"
        Retry = [
          {
            ErrorEquals = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts = 3
            BackoffRate = 2.0
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath = "$.error"
            Next = "EmbeddingFailed"
          }
        ]
      }
      "EmbeddingSucceeded?" = {
        Type = "Choice"
        Choices = [
          {
            Variable = "$.embeddingResult.statusCode"
            NumericEquals = 200
            Next = "ProcessingSucceeded"
          }
        ]
        Default = "EmbeddingFailed"
      }
      ProcessingSucceeded = {
        Type = "Succeed"
      }
      TranscribeFailed = {
        Type = "Fail"
        Error = "TranscriptionError"
        Cause = "Transcription processing failed"
      }
      ChunkingFailed = {
        Type = "Fail"
        Error = "ChunkingError"
        Cause = "Chunking processing failed"
      }
      EmbeddingFailed = {
        Type = "Fail"
        Error = "EmbeddingError"
        Cause = "Embedding processing failed"
      }
    }
  })

  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}

# Create a bucket for CloudTrail logs
module "cloudtrail_logs_bucket" {
  source = "../../modules/s3"
  
  bucket_name = "dev-video-pipeline-cloudtrail-logs"
  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}

# CloudTrail bucket policy to allow CloudTrail to write logs
resource "aws_s3_bucket_policy" "cloudtrail_bucket_policy" {
  bucket = module.cloudtrail_logs_bucket.bucket_id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AWSCloudTrailAclCheck"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:GetBucketAcl"
        Resource  = module.cloudtrail_logs_bucket.bucket_arn
      },
      {
        Sid       = "AWSCloudTrailWrite"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${module.cloudtrail_logs_bucket.bucket_arn}/AWSLogs/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# Enable S3 CloudTrail for EventBridge integration
resource "aws_cloudtrail" "s3_cloudtrail" {
  name                          = "dev-s3-cloudtrail"
  s3_bucket_name                = module.cloudtrail_logs_bucket.bucket_id
  include_global_service_events = true
  is_multi_region_trail        = false
  enable_logging               = true
  depends_on                   = [aws_s3_bucket_policy.cloudtrail_bucket_policy]

  advanced_event_selector {
    name = "Log S3 object-level events"

    field_selector {
      field  = "eventCategory"
      equals = ["Data"]
    }

    field_selector {
      field = "resources.type"
      equals = ["AWS::S3::Object"]
    }

    field_selector {
      field = "resources.ARN"
      starts_with = ["${module.media_bucket.bucket_arn}/"]
    }
  }

  advanced_event_selector {
    name = "Log management events"
    field_selector {
      field  = "eventCategory"
      equals = ["Management"]
    }
  }

  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}

# Update EventBridge Rule to capture S3 events via CloudTrail
resource "aws_cloudwatch_event_rule" "s3_input_rule" {
  name        = "dev-media-input-rule"
  description = "Capture S3 events from media input bucket"

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventSource = ["s3.amazonaws.com"]
      eventName   = ["PutObject", "CompleteMultipartUpload"]
      requestParameters = {
        bucketName = [module.media_bucket.bucket_id]
      }
    }
  })

  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}

# EventBridge Target for Step Functions
resource "aws_cloudwatch_event_target" "sfn_target" {
  rule      = aws_cloudwatch_event_rule.s3_input_rule.name
  target_id = "StepFunctionsTarget"
  arn       = aws_sfn_state_machine.video_processing.arn
  role_arn  = aws_iam_role.eventbridge_role.arn
}

module "audio_segments_queue" {
  source = "../../modules/sqs"
  
  environment     = "dev"
  lambda_role_name = module.chunking_lambda.role_name
}

# Outputs
output "media_bucket_name" {
  value = module.media_bucket.bucket_id
}

output "transcription_bucket_name" {
  value = module.transcription_bucket.bucket_id
}

output "transcribe_lambda_function_name" {
  value = module.transcribe_lambda.function_name
}

output "chunking_lambda_function_name" {
  value = module.chunking_lambda.function_name
}

output "embedding_lambda_function_name" {
  description = "Name of the embedding Lambda function"
  value       = module.lambda_embedding.function_name
}

output "sfn_state_machine_arn" {
  value = aws_sfn_state_machine.video_processing.arn
}

output "eventbridge_rule_arn" {
  value = aws_cloudwatch_event_rule.s3_input_rule.arn
} 
resource "aws_sqs_queue" "audio_segments_queue" {
  name                      = "audio_segments_queue"
  delay_seconds             = 0
  max_message_size         = 262144  # 256 KB
  message_retention_seconds = 345600  # 4 days
  receive_wait_time_seconds = 0
  visibility_timeout_seconds = 30
  
  tags = {
    Environment = var.environment
    Project     = "video-pipeline"
  }
}

# IAM policy for Lambda to access SQS
data "aws_iam_policy_document" "lambda_sqs_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:GetQueueUrl",
      "sqs:GetQueueAttributes"
    ]
    resources = [aws_sqs_queue.audio_segments_queue.arn]
  }
}

# Create the IAM policy
resource "aws_iam_policy" "lambda_sqs_policy" {
  name        = "${var.environment}_lambda_sqs_policy"
  description = "IAM policy for Lambda to access SQS queue"
  policy      = data.aws_iam_policy_document.lambda_sqs_policy.json
}

# Attach the policy to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_sqs_policy" {
  role       = var.lambda_role_name
  policy_arn = aws_iam_policy.lambda_sqs_policy.arn
} 
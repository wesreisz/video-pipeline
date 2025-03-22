## Prompt: Add SQS Queue Integration for `audio_segments` in AWS Lambda.  The name of this sqs queue should be `audio_segments_queue`.

### Prerequisites (MUST BE COMPLETED FIRST)
Before implementing the SQS integration, verify these prerequisites are met:

1. **Lambda Module Requirements**
   The Lambda module in `infra/modules/lambda/outputs.tf` MUST have these exact outputs:
   ```hcl
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

   output "role_name" {  # CRITICAL: Must exist before proceeding
     description = "Name of the IAM role"
     value       = aws_iam_role.lambda_role.name
   }
   ```

   ⚠️ **STOP AND UPDATE LAMBDA MODULE FIRST**: If `role_name` output is missing, update the Lambda module before proceeding.

### Implementation Tasks (Only proceed after prerequisites are met)

1. **Create SQS Module**
   Create a new SQS module with the following components:

   a. **Queue Resource** (`infra/modules/sqs/main.tf`):
   ```hcl
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
   ```

   b. **IAM Policy Document and Attachment** (`infra/modules/sqs/main.tf`):
   ```hcl
   # IAM policy document for Lambda to access SQS
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
   ```

   c. **Variables** (`infra/modules/sqs/variables.tf`):
   ```hcl
   variable "environment" {
     description = "Environment name (e.g., dev, prod)"
     type        = string
   }

   variable "lambda_role_name" {
     description = "Name of the Lambda IAM role to attach SQS permissions"
     type        = string
   }
   ```

2. **Lambda Handler Updates** (`modules/chunking-module/src/handlers/chunking_handler.py`)
   - Add environment variable check:
     ```python
     SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')
     if not SQS_QUEUE_URL:
         raise ValueError("SQS_QUEUE_URL environment variable is not set")
     ```
   - Implement SQS sending functionality:
     ```python
     def send_to_sqs(audio_segments: List[AudioSegment]) -> int:
         """Send audio segments to SQS queue."""
         sqs_client = boto3.client('sqs')
         sent_count = 0
         
         for segment in audio_segments:
             try:
                 response = sqs_client.send_message(
                     QueueUrl=SQS_QUEUE_URL,
                     MessageBody=json.dumps(segment)
                 )
                 sent_count += 1
                 logger.info(f"Sent segment to SQS: MessageId={response['MessageId']}")
             except Exception as e:
                 logger.error(f"Failed to send segment to SQS: {str(e)}")
                 raise
         
         return sent_count
     ```
   - Update response to include segments sent count:
     ```python
     response_data = {
         'message': 'Chunking completed successfully',
         'segments_sent': sent_count,
         'note': 'Audio segments have been sent to SQS queue'
     }
     ```

### Validation Steps
Before applying changes:
1. ✓ Verify Lambda module has `role_name` output
2. ✓ Verify all required SQS module outputs are defined
3. ✓ Verify IAM policy document is created and attached to Lambda role
4. ✓ Verify environment variables are correctly set
5. ✓ Verify Python handler has proper error handling

### Expected Outputs
- Successful SQS message sending with logging
- Proper error handling and reporting
- Complete infrastructure setup with all dependencies
- IAM policy attached to Lambda role with correct permissions

### Reference Files
- `terraform.mdc` - SQS Module Standards
- `infra/environments/dev/main.tf`
- `modules/chunking-module/src/handlers/chunking_handler.py`
- `infra/modules/lambda/outputs.tf`
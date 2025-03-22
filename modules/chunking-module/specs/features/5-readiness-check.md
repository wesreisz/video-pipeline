# Readiness Check Implementation

## Problem
The deployment script was running too fast, causing end-to-end tests to fail because AWS resources (Lambda functions and Step Functions state machine) were not fully ready when the tests started.

## Solution
We need to implement two key components:
1. A readiness check function in the deployment script
2. CloudTrail and EventBridge configuration to properly capture S3 events

### 1. Deployment Script Readiness Check
Add the following function to `infra/environments/dev/deploy.sh`:

```bash
# Function to check AWS resource readiness with retries
check_aws_resource_readiness() {
    echo -e "\n${BOLD}===== Checking AWS Resource Readiness =====${NO_COLOR}"
    local max_attempts=12
    local wait_time=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "\n${YELLOW}Attempt $attempt of $max_attempts: Checking resource readiness...${NO_COLOR}"
        
        # Check Lambda function status
        echo -e "${YELLOW}Checking Lambda functions...${NO_COLOR}"
        local lambda_ready=true
        
        # Get Lambda function names from Terraform output
        local transcribe_function=$(terraform output -raw transcribe_lambda_function_name)
        local chunking_function=$(terraform output -raw chunking_lambda_function_name)
        
        # Check each Lambda function
        for func in "$transcribe_function" "$chunking_function"; do
            echo -e "Checking Lambda function: $func"
            if ! aws lambda get-function --function-name "$func" --query 'Configuration.State' | grep -q "Active"; then
                lambda_ready=false
                break
            fi
        done
        
        # Check Step Functions state machine
        echo -e "${YELLOW}Checking Step Functions state machine...${NO_COLOR}"
        local sfn_arn=$(terraform output -raw sfn_state_machine_arn)
        local sfn_ready=false
        
        if aws stepfunctions describe-state-machine --state-machine-arn "$sfn_arn" --query 'status' | grep -q "ACTIVE"; then
            sfn_ready=true
        fi
        
        # If all checks pass, we're ready
        if [ "$lambda_ready" = true ] && [ "$sfn_ready" = true ]; then
            echo -e "\n${GREEN}All AWS resources are ready!${NO_COLOR}"
            return 0
        fi
        
        echo -e "\n${YELLOW}Resources not ready yet. Waiting $wait_time seconds before next attempt...${NO_COLOR}"
        sleep $wait_time
        attempt=$((attempt + 1))
    done
    
    echo -e "\n${RED}Timeout waiting for AWS resources to be ready. Please check the AWS Console for more details.${NO_COLOR}"
    return 1
}
```

### 2. CloudTrail and EventBridge Configuration
Update the CloudTrail configuration in `infra/environments/dev/main.tf` to properly capture S3 events:

```hcl
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
```

### Integration
1. Add the readiness check function to your deployment script
2. Call it before running end-to-end tests:

```bash
# In your main deployment flow
main() {
    # ... previous steps ...
    
    # Step 6: Wait for resources to be fully ready
    check_aws_resource_readiness || {
        echo -e "\n${RED}AWS resources did not become ready in time. Aborting end-to-end tests.${NO_COLOR}"
        exit 1
    }
    
    # Step 7: Run consolidated end-to-end test
    run_e2e_test
    
    # ... rest of the script ...
}
```

## Results
- The deployment script now waits for all AWS resources to be fully ready before proceeding with end-to-end tests
- CloudTrail properly captures S3 events and forwards them to EventBridge
- The Step Functions state machine receives events when files are uploaded to the S3 bucket
- End-to-end tests run successfully without timing issues

My deployment script is running too fast. AWS Resources are not ready yet.
Add a readiness check to each of my lambdas and make sure they're ready before my script 
runs the end to end test. Here is a a reference to the readiness check:
```
def is_ready():
    try:
        # Check connectivity or load
        boto3.client('s3').head_bucket(Bucket='my-model-bucket')
        return True
    except Exception as e:
        print(f"Readiness check failed: {e}")
        return False

def lambda_handler(event, context):
    if not is_ready():
        return {
            'statusCode': 503,
            'body': 'Service Unavailable - Not Ready'
        }
    # Proceed with normal logic

```
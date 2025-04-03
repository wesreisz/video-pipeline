#!/bin/bash

# Script to create an IAM user with access to specific S3 bucket
# Usage: ./create_s3_user.sh <developer-name>

# Set the developer's username - you can pass this as an argument or change it here
DEVELOPER_NAME=${1:-"new-developer"}
BUCKET_NAME="dev-media-transcribe-input"

echo "Creating IAM user and access for $DEVELOPER_NAME..."

# Create the IAM user
aws iam create-user --user-name "$DEVELOPER_NAME"

# Create access key and save the output
ACCESS_KEY_OUTPUT=$(aws iam create-access-key --user-name "$DEVELOPER_NAME")

# Extract access key and secret from the JSON output
ACCESS_KEY_ID=$(echo $ACCESS_KEY_OUTPUT | jq -r .AccessKey.AccessKeyId)
SECRET_ACCESS_KEY=$(echo $ACCESS_KEY_OUTPUT | jq -r .AccessKey.SecretAccessKey)

# Create the policy document for S3 access
aws iam put-user-policy \
    --user-name "$DEVELOPER_NAME" \
    --policy-name "S3Access" \
    --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::'"$BUCKET_NAME"'",
                "arn:aws:s3:::'"$BUCKET_NAME"'/*"
            ]
        }
    ]
}'

# Output the credentials in a clear format
echo "=========================================="
echo "Access credentials for $DEVELOPER_NAME:"
echo "=========================================="
echo "AWS Access Key ID: $ACCESS_KEY_ID"
echo "AWS Secret Access Key: $SECRET_ACCESS_KEY"
echo "=========================================="
echo ""
echo "Instructions for the developer:"
echo "1. Install the AWS CLI if not already installed"
echo "2. Run the following commands to configure:"
echo ""
echo "aws configure"
echo "AWS Access Key ID: [Use the Access Key ID above]"
echo "AWS Secret Access Key: [Use the Secret Access Key above]"
echo "Default region name: [your-region]"
echo "Default output format: json"
echo ""
echo "3. Test access with:"
echo "aws s3 ls s3://$BUCKET_NAME"
echo "==========================================" 
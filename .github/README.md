# GitHub Actions Setup for Video Pipeline

This repository includes a GitHub Actions workflow to automatically deploy your video pipeline when code is pushed to the repository.

## Workflow

**`deploy.yml`** - Deployment workflow that runs tests, builds Lambda packages, and deploys using Terraform

## Setup Instructions

### 1. AWS Authentication Setup

**Important Security Practice**: Create a dedicated IAM user for GitHub Actions deployments. This user should have the minimum permissions required for deployment.

#### Step 1: Create Dedicated CI/CD User

1. **Create a new IAM user specifically for GitHub Actions**:
   ```bash
   aws iam create-user --user-name github-actions-video-pipeline
   ```

2. **Create a custom policy file** (`video-pipeline-ci-cd-policy.json`):
   ```bash
   cat > video-pipeline-ci-cd-policy.json << 'EOF'
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "lambda:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "iam:CreateRole",
           "iam:DeleteRole",
           "iam:GetRole",
           "iam:ListRolePolicies",
           "iam:ListAttachedRolePolicies",
           "iam:PassRole",
           "iam:CreatePolicy",
           "iam:DeletePolicy",
           "iam:GetPolicy",
           "iam:GetPolicyVersion",
           "iam:ListPolicyVersions",
           "iam:AttachRolePolicy",
           "iam:DetachRolePolicy",
           "iam:TagRole",
           "iam:UntagRole",
           "iam:TagPolicy",
           "iam:UntagPolicy"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "states:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "events:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "logs:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "apigateway:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "transcribe:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "secretsmanager:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "kms:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "sqs:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "cloudtrail:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "dynamodb:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "acm:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "route53:*"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "ec2:DescribeAvailabilityZones",
           "ec2:DescribeVpcs",
           "ec2:DescribeSubnets",
           "ec2:DescribeSecurityGroups",
           "ec2:DescribeNetworkInterfaces"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "sts:GetCallerIdentity"
         ],
         "Resource": "*"
       }
     ]
   }
   EOF
   ```

3. **Create the IAM policy**:
   ```bash
   aws iam create-policy \
     --policy-name VideoPipelineCI-CD-Policy \
     --policy-document file://video-pipeline-ci-cd-policy.json \
     --description "Least-privilege policy for GitHub Actions video pipeline deployment"
   ```

4. **Get your AWS account ID** (needed for the next step):
   ```bash
   AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   echo "Your AWS Account ID: $AWS_ACCOUNT_ID"
   ```

5. **Attach the policy to the user**:
   ```bash
   aws iam attach-user-policy \
     --user-name github-actions-video-pipeline \
     --policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/VideoPipelineCI-CD-Policy
   ```

6. **Generate access keys for GitHub Actions**:
   ```bash
   aws iam create-access-key --user-name github-actions-video-pipeline
   ```
   
   **⚠️ Important**: Save the `AccessKeyId` and `SecretAccessKey` from this output - you'll need them for GitHub secrets and **they won't be shown again**.

#### Step 2: Verify User Setup

7. **Verify the user was created correctly**:
   ```bash
   # Check user exists
   aws iam get-user --user-name github-actions-video-pipeline
   
   # Check policy is attached
   aws iam list-attached-user-policies --user-name github-actions-video-pipeline
   ```

### 2. Required Repository Secrets

Go to your repository Settings → Secrets and variables → Actions, and add:

#### Required Secrets:
- `AWS_ACCESS_KEY_ID`: Access Key ID from the `github-actions-video-pipeline` user (from step 6 above)
- `AWS_SECRET_ACCESS_KEY`: Secret Access Key from the `github-actions-video-pipeline` user (from step 6 above)
- `AWS_REGION`: Your AWS region (e.g., `us-east-1`)
- `OPENAI_API_KEY`: Your OpenAI API key for embedding generation (starts with `sk-proj-...` or `sk-...`)
- `PINECONE_API_KEY`: Your Pinecone API key for vector database access (starts with `pcsk_...`)

#### Optional Secrets:
- `CERTIFICATE_DOMAIN`: Your custom domain for SSL certificates (defaults to `icaet-dev.wesleyreisz.com`)

### 3. User Separation Best Practices

**Local Development**: Continue using your existing admin user (`qcon-ciaet-admin`) for:
- ✅ Manual AWS Console access
- ✅ Local terraform testing and development
- ✅ Administrative tasks requiring elevated permissions
- ✅ One-time setup and configuration

**GitHub Actions CI/CD**: Use the new `github-actions-video-pipeline` user for:
- ✅ Automated deployments
- ✅ CI/CD pipeline operations
- ✅ Scheduled maintenance tasks
- ✅ Any automated AWS API calls

**Why This Separation Matters**:
- 🔒 **Reduced blast radius**: If GitHub is compromised, attacker can only access video pipeline resources
- 📊 **Better auditing**: Clear separation in CloudTrail logs between manual and automated actions
- 🔑 **Easier key rotation**: Can rotate CI/CD keys without affecting local development
- 📋 **Compliance**: Follows security best practices for least-privilege access

### 4. Required AWS Permissions Summary

The custom policy provides permissions for deploying all components of the video pipeline including:
- **S3**: Media storage, transcription output, access lists, CloudTrail logs
- **Lambda**: All four microservices (transcribe, chunking, embedding, question)
- **IAM**: Roles and policies for service permissions (limited scope)
- **Step Functions**: Video processing workflow orchestration
- **EventBridge**: S3 event triggers for the pipeline
- **CloudWatch Logs**: Application logging
- **API Gateway**: Question module REST API
- **Transcribe**: Audio transcription service
- **Secrets Manager**: Secure storage of API keys
- **KMS**: Encryption key management
- **SQS**: Message queuing for processing
- **CloudTrail**: S3 event logging
- **DynamoDB**: Terraform state locking
- **ACM & Route53**: SSL certificate management

## Workflow Triggers

The deployment workflow:
- Triggers on push to `main` or `master` branch
- Triggers on merged pull requests to `main` or `master`
- Can be manually triggered via GitHub UI (Actions tab → Deploy Video Pipeline → Run workflow)

## What the Workflow Does

1. **Environment Setup**: Sets up Python 3.11, AWS CLI, and Terraform
2. **Testing**: Runs tests for all four modules (transcribe, chunking, embedding, question)
3. **Building**: Creates Lambda deployment packages and layers
4. **Infrastructure**: Deploys AWS infrastructure using Terraform
5. **Validation**: Runs end-to-end tests to verify the deployment
6. **Artifacts**: Saves deployment logs and Terraform state for troubleshooting

## Customization

### Adding Notifications

You can add Slack, Teams, or email notifications by adding steps like:

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Adding Security Scanning

You can enhance the workflow with security scanning tools:

- **Bandit**: For Python security scanning
- **Safety**: For dependency vulnerability scanning
- **Checkov**: For Terraform security scanning

Example addition to the workflow:
```yaml
- name: Security scan
  run: |
    pip install bandit safety
    bandit -r modules/
    safety check
```

## Troubleshooting

### Common Issues

1. **AWS Permissions Error**: Ensure the `github-actions-video-pipeline` user has the correct policy attached
2. **Terraform State Lock**: Check if another deployment is running
3. **Python Dependencies**: Ensure all `requirements.txt` files are up to date
4. **Environment Variables**: Verify all required secrets are set with the correct user's credentials

### Debug Mode

To enable debug logging, add this to your workflow:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

### Manual Deployment

You can always run the deployment script manually using your admin user:

```bash
cd infra/environments/dev
./deploy.sh
```

### Viewing Deployment Logs

1. Go to your repository's Actions tab
2. Click on the latest workflow run
3. Expand the steps to see detailed logs
4. Download artifacts for Terraform state and build files

## Security Best Practices

1. **Use dedicated users for different purposes** (admin vs CI/CD)
2. **Regularly rotate access keys** for the CI/CD user (every 90 days)
3. **Monitor CloudTrail logs** for both users separately
4. **Use least-privilege permissions** (as implemented in this setup)
5. **Store Terraform state remotely** with encryption
6. **Never commit credentials** to your repository
7. **Review deployment logs** regularly for anomalies

## Key Rotation

To rotate the GitHub Actions credentials:

```bash
# 1. Create new access key
aws iam create-access-key --user-name github-actions-video-pipeline

# 2. Update GitHub secrets with new credentials
# 3. Delete old access key (get the old key ID first)
aws iam list-access-keys --user-name github-actions-video-pipeline
aws iam delete-access-key --user-name github-actions-video-pipeline --access-key-id OLD_KEY_ID
```

## Monitoring

After deployment, monitor your resources:

- CloudWatch for Lambda function logs
- X-Ray for distributed tracing
- AWS Cost Explorer for cost monitoring
- Step Functions execution history 
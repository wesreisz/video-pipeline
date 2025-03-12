# Creating Bootstrap Terraform Configuration for State Management

## Task: Create a Terraform bootstrap configuration to set up S3 and DynamoDB for state management

Follow these steps to create a separate bootstrap Terraform configuration that will set up the necessary resources for managing Terraform state:

1. Create the bootstrap directory structure inside your infra folder:
```bash
mkdir -p infra/bootstrap
```

2. Create the following files in the bootstrap directory:
   - main.tf
   - variables.tf
   - outputs.tf

3. In main.tf, define the AWS provider and resources for state management:
```terraform
provider "aws" {
  region = var.region
}

# S3 bucket for storing Terraform state
resource "aws_s3_bucket" "terraform_state" {
  bucket = "${var.project_name}-terraform-state-${var.environment}"
  
  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }
}

# Enable versioning for state files
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "${var.project_name}-terraform-locks-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
}
```

4. In variables.tf, define the necessary variables:
```terraform
variable "region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  default     = "video-pipeline"
}

variable "environment" {
  description = "Environment (dev, prod, etc.)"
  default     = "dev"
}
```

5. In outputs.tf, define outputs to easily reference the created resources:
```terraform
output "s3_bucket_name" {
  value = aws_s3_bucket.terraform_state.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.terraform_locks.name
}
```

6. Initialize and apply the bootstrap configuration:
```bash
cd infra/bootstrap
terraform init
terraform apply
```

7. After successfully creating the state resources, configure your environment-specific Terraform configurations to use them. For example, in infra/environments/dev/main.tf:
```terraform
terraform {
  backend "s3" {
    bucket         = "video-pipeline-terraform-state-dev"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "video-pipeline-terraform-locks-dev"
    encrypt        = true
  }
}

# Rest of your dev environment configuration...
```

8. Initialize your dev environment configuration with the new backend:
```bash
cd infra/environments/dev
terraform init
```

Now you have a properly set up Terraform state management system using S3 for state storage and DynamoDB for state locking!

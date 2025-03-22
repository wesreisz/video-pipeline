variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "lambda_role_name" {
  description = "Name of the Lambda IAM role to attach SQS permissions"
  type        = string
} 
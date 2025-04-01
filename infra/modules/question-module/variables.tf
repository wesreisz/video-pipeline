variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "log_level" {
  description = "Log level for the Lambda function"
  type        = string
  default     = "INFO"
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

variable "secrets_access_policy_arn" {
  description = "ARN of the IAM policy for accessing secrets"
  type        = string
} 
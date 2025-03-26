variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "openai_api_key" {
  description = "API key for OpenAI service"
  type        = string
  sensitive   = true
}

variable "pinecone_api_key" {
  description = "API key for Pinecone service"
  type        = string
  sensitive   = true
}

variable "log_level" {
  description = "Log level for Lambda function"
  type        = string
  default     = "INFO"
}

variable "sqs_queue_url" {
  description = "URL of the SQS queue to process"
  type        = string
}

variable "sqs_queue_arn" {
  description = "ARN of the SQS queue to process"
  type        = string
}

variable "sqs_batch_size" {
  description = "Number of records to process in each batch"
  type        = number
  default     = 10
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}

variable "secrets_access_policy_arn" {
  description = "ARN of the IAM policy for accessing secrets"
  type        = string
}

variable "max_concurrency" {
  description = "Maximum number of concurrent Lambda instances for SQS processing (min: 2, max: 1000)"
  type        = number
  default     = 10
} 
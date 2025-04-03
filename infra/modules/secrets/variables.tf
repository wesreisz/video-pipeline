variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "pinecone_api_key" {
  description = "Pinecone API Key"
  type        = string
  sensitive   = true
}

variable "log_level" {
  description = "Log level for the application"
  type        = string
  default     = "INFO"
}

variable "sqs_queue_url" {
  description = "URL of the SQS queue"
  type        = string
}

variable "video_pipeline_api_key" {
  description = "Video Pipeline API Key (optional - will be auto-generated if not provided)"
  type        = string
  sensitive   = true
  default     = null
} 
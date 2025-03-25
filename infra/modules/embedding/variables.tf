variable "openai_api_key" {
  description = "OpenAI API key for embedding service"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "video-pipeline"
} 
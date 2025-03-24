variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "video-pipeline"
}

variable "openai_api_key" {
  description = "API key for OpenAI service"
  type        = string
  sensitive   = true
  default     = "placeholder-openai-api-key"
}

variable "pinecone_api_key" {
  description = "API key for Pinecone service"
  type        = string
  sensitive   = true
  default     = "placeholder-pinecone-api-key"
} 
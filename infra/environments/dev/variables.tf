variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "video-pipeline"
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

variable "video_pipeline_api_key" {
  description = "Video Pipeline API Key (optional - will be auto-generated if not provided)"
  type        = string
  sensitive   = true
  default     = null
}

variable "certificate_domain" {
  description = "Domain name for the AWS Certificate"
  type        = string
  default     = "your-domain.com"  # Replace with your actual domain
} 
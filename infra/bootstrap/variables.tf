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
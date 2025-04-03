variable "domain_name" {
  description = "The domain name for the API Gateway custom domain"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "api_gateway_id" {
  description = "The ID of the API Gateway API"
  type        = string
}

variable "stage_name" {
  description = "The name of the API Gateway stage"
  type        = string
} 
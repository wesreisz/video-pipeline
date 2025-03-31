resource "aws_ssm_parameter" "openai_api_key" {
  name        = "/${var.project_name}/${var.environment}/openai_api_key"
  description = "OpenAI API key for embedding service"
  type        = "SecureString"
  value       = var.openai_api_key
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
    Service     = "embedding"
  }
}

# Output the SSM parameter name for reference
output "openai_api_key_parameter" {
  description = "SSM parameter name for OpenAI API key"
  value       = aws_ssm_parameter.openai_api_key.name
} 
output "function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda.function_name
}

output "function_arn" {
  description = "ARN of the Lambda function"
  value       = module.lambda.function_arn
}

output "role_name" {
  description = "Name of the Lambda IAM role"
  value       = module.lambda.role_name
}

output "role_arn" {
  description = "ARN of the Lambda IAM role"
  value       = module.lambda.role_arn
} 
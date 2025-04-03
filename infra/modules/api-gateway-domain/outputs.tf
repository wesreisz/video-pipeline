output "domain_name" {
  description = "The custom domain name"
  value       = aws_api_gateway_domain_name.api.domain_name
}

output "certificate_arn" {
  description = "The ARN of the ACM certificate"
  value       = aws_acm_certificate.api_cert.arn
}

output "api_gateway_domain_name" {
  description = "The API Gateway domain name configuration"
  value       = aws_api_gateway_domain_name.api.regional_domain_name
} 
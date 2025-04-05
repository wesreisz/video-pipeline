output "domain_name" {
  description = "The custom domain name"
  value       = aws_api_gateway_domain_name.api.domain_name
}

output "certificate_arn" {
  description = "The ARN of the ACM certificate"
  value       = module.certificate.certificate_arn
}

output "api_gateway_domain_name" {
  description = "The API Gateway domain name configuration"
  value       = aws_api_gateway_domain_name.api.regional_domain_name
}

output "dns_validation_records" {
  description = "DNS records needed for certificate validation (if new certificate was created)"
  value       = module.certificate.dns_validation_records
} 
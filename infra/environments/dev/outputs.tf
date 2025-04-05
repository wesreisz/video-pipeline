# Outputs have been moved to main.tf 

output "access_list_bucket_name" {
  description = "The name of the S3 bucket storing the access list"
  value       = module.access_list_bucket.bucket_id
}

output "api_gateway_domain_name" {
  description = "The API Gateway domain name configuration"
  value       = module.api_gateway_domain.api_gateway_domain_name
}

output "api_gateway_dns_validation_records" {
  description = "DNS records needed for certificate validation"
  value       = module.api_gateway_domain.dns_validation_records
} 
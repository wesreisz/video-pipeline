output "certificate_arn" {
  description = "ARN of the certificate"
  value       = aws_acm_certificate.new.arn
}

output "certificate_domain" {
  description = "Domain name of the certificate"
  value       = var.domain_name
}

output "is_new_certificate" {
  description = "Whether a new certificate was created"
  value       = length(aws_acm_certificate.new) > 0
}

output "dns_validation_records" {
  description = "DNS records needed for certificate validation"
  value = {
    for dvo in aws_acm_certificate.new.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
} 
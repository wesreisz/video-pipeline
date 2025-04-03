terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version              = "~> 5.0"
      configuration_aliases = [aws.us-east-1]
    }
  }
}

# Create ACM Certificate
resource "aws_acm_certificate" "api_cert" {
  provider          = aws.us-east-1  # ACM certificates for API Gateway must be in us-east-1
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Environment = var.environment
  }
}

# Output the DNS validation records that need to be created in GoDaddy
output "certificate_validation_records" {
  value = {
    for dvo in aws_acm_certificate.api_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
}

# Create API Gateway domain name (REST API)
resource "aws_api_gateway_domain_name" "api" {
  provider          = aws.us-east-1
  domain_name       = var.domain_name
  certificate_arn   = aws_acm_certificate.api_cert.arn
  security_policy   = "TLS_1_2"

  endpoint_configuration {
    types = ["EDGE"]
  }
}

# Create base path mapping
resource "aws_api_gateway_base_path_mapping" "api" {
  provider    = aws.us-east-1
  api_id      = var.api_gateway_id
  domain_name = aws_api_gateway_domain_name.api.domain_name
  stage_name  = var.stage_name
} 
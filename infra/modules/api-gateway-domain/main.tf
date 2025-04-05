terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version              = "~> 5.0"
      configuration_aliases = [aws.us-east-1]
    }
  }
}

# Use the certificate module to manage the certificate
module "certificate" {
  source = "../certificate"
  
  domain_name       = var.domain_name
  create_if_missing = true  # Will create new certificate if none exists
  
  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }

  providers = {
    aws = aws.us-east-1  # ACM certificates for API Gateway must be in us-east-1
  }
}

# Create API Gateway domain name
resource "aws_api_gateway_domain_name" "api" {
  provider                = aws.us-east-1
  domain_name            = var.domain_name
  regional_certificate_arn = module.certificate.certificate_arn
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  depends_on = [module.certificate]
}

# Create base path mapping
resource "aws_api_gateway_base_path_mapping" "api" {
  provider    = aws.us-east-1
  api_id      = var.api_gateway_id
  domain_name = aws_api_gateway_domain_name.api.domain_name
  stage_name  = var.stage_name
} 
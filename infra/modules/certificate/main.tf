terraform {
  required_version = ">= 1.5.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Create new certificate
resource "aws_acm_certificate" "new" {
  domain_name               = var.domain_name
  validation_method         = "DNS"
  subject_alternative_names = var.subject_alternative_names

  tags = merge(var.tags, {
    Name = "${var.domain_name}-certificate"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Protection resource to prevent accidental deletion
resource "aws_acm_certificate_validation" "protection" {
  certificate_arn = aws_acm_certificate.new.arn

  lifecycle {
    prevent_destroy = true
  }
} 
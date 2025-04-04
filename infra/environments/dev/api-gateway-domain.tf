module "api_gateway_domain" {
  source = "../../modules/api-gateway-domain"
  
  providers = {
    aws.us-east-1 = aws.us-east-1
  }

  domain_name    = "icaet-dev.wesleyreisz.com"
  environment    = "dev"
  api_gateway_id = module.question_module.api_id
  stage_name     = "dev"
} 
# Certificate Protection Module

This module manages AWS ACM certificates with protection against accidental deletion. It can either use an existing certificate or create a new one if none exists.

## Features

- Looks up existing certificates by domain name
- Creates new certificates if none exist (with DNS validation)
- Prevents accidental deletion using lifecycle policies
- Supports multiple domains via subject alternative names
- Provides DNS validation records for manual configuration
- Supports tagging

## Usage

```hcl
# Using existing certificate or creating new one
module "certificate_protection" {
  source = "../../modules/certificate"

  domain_name       = "example.com"
  create_if_missing = true  # Will create new certificate if none exists
  
  subject_alternative_names = ["*.example.com"]  # Optional
  tags = {
    Environment = "dev"
    Project     = "video-pipeline"
  }
}

# After applying, you'll get DNS validation records to add to your DNS provider:
output "dns_records" {
  value = module.certificate_protection.dns_validation_records
}
```

## DNS Validation Process

When a new certificate is created, you'll need to:

1. Apply the Terraform configuration
2. Get the DNS validation records from the outputs
3. Add these records to your DNS provider (e.g., GoDaddy):
   ```hcl
   # Example output format
   dns_validation_records = {
     "example.com" = {
       name  = "_acme-challenge.example.com"
       type  = "CNAME"
       value = "validation.aws.com"
     }
   }
   ```
4. Wait for DNS propagation and certificate validation (can take 30+ minutes)

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 5.91.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| domain_name | Domain name for the AWS Certificate | `string` | n/a | yes |
| create_if_missing | Whether to create a new certificate if none exists | `bool` | `true` | no |
| subject_alternative_names | Additional domain names to add to the certificate | `list(string)` | `[]` | no |
| tags | Tags to apply to resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| certificate_arn | ARN of the certificate (either existing or newly created) |
| certificate_domain | Domain name of the certificate |
| is_new_certificate | Whether a new certificate was created |
| dns_validation_records | DNS records needed for certificate validation |

## Certificate Creation Process

When `create_if_missing = true`:

1. Module first searches for an existing certificate
2. If none found, creates a new certificate with DNS validation
3. Outputs the required DNS validation records
4. You must manually add these records to your DNS provider
5. AWS will validate the certificate once DNS records propagate
6. Applies deletion protection

## Important Notes

1. **DNS Validation**: 
   - You must manually add the DNS records to your DNS provider
   - DNS propagation can take 30+ minutes
   - Certificate validation won't complete until DNS records are properly set

2. **Certificate Protection**:
   This module uses the `prevent_destroy` lifecycle policy to protect certificates from accidental deletion. To actually delete a certificate:
   - Remove the `prevent_destroy` block from the module's `main.tf`
   - Run `terraform apply` to update the state
   - Run `terraform destroy`

Always verify you're working with the correct certificate before attempting deletion.

## Error Handling

The module will fail gracefully with a clear error message if:
- No certificate is found for the specified domain
- The certificate exists but is not in ISSUED state
- Multiple certificates exist (it will use the most recent one) 
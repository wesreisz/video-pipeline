variable "domain_name" {
  description = "Domain name for the AWS Certificate"
  type        = string
}

variable "create_if_missing" {
  description = "Whether to create a new certificate if one doesn't exist"
  type        = bool
  default     = true
}

variable "subject_alternative_names" {
  description = "Additional domain names to add to the certificate"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
} 
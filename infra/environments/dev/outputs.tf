# Outputs have been moved to main.tf 

output "access_list_bucket_name" {
  description = "Name of the S3 bucket storing the access list"
  value       = module.access_list_bucket.bucket_id
} 
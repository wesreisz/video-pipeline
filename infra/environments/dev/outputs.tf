output "video_storage_bucket_name" {
  description = "Name of the S3 bucket for video storage"
  value       = module.video_storage_bucket.bucket_id
}

output "video_storage_bucket_arn" {
  description = "ARN of the S3 bucket for video storage"
  value       = module.video_storage_bucket.bucket_arn
} 
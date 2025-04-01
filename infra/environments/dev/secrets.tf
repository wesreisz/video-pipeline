module "secrets" {
  source = "../../modules/secrets"

  environment     = "dev"
  openai_api_key  = var.openai_api_key
  pinecone_api_key = var.pinecone_api_key
  video_pipeline_api_key = var.video_pipeline_api_key
  log_level        = "INFO"
  sqs_queue_url    = module.audio_segments_queue.queue_url
}

# Export the secrets access policy ARN for use in other modules
output "secrets_access_policy_arn" {
  description = "ARN of the IAM policy for accessing secrets"
  value       = module.secrets.secrets_access_policy_arn
} 
terraform {
  backend "s3" {
    bucket         = "video-pipeline-terraform-state"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "video-pipeline-terraform-locks-dev"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = "dev"
      Project     = "video-pipeline"
      ManagedBy   = "terraform"
    }
  }
}

# S3 bucket for storing video files
module "video_storage_bucket" {
  source = "../../modules/s3"

  bucket_name       = "${var.project_name}-video-storage-${var.environment}"
  enable_versioning = true
  tags = {
    Description = "Storage for video files that need to be processed"
    Service     = "Video Storage"
  }
} 
variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "handler" {
  description = "Handler function for Lambda"
  type        = string
}

variable "runtime" {
  description = "Runtime for Lambda function"
  type        = string
  default     = "python3.9"
}

variable "timeout" {
  description = "Timeout in seconds"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Memory size in MB"
  type        = number
  default     = 128
}

variable "source_dir" {
  description = "Directory of source code to be zipped"
  type        = string
}

variable "output_path" {
  description = "Path where the zip file will be created"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables for Lambda function"
  type        = map(string)
  default     = {}
}

variable "s3_bucket_arns" {
  description = "List of S3 bucket ARNs the Lambda needs access to"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
} 
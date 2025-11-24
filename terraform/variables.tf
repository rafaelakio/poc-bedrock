variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "bedrock-ocr"
}

variable "ocr_model_id" {
  description = "Bedrock model ID for OCR"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "embedding_model_id" {
  description = "Bedrock model ID for embeddings"
  type        = string
  default     = "amazon.titan-embed-text-v1"
}

variable "validation_model_id" {
  description = "Bedrock model ID for validation"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 900
}

variable "lambda_memory" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 2048
}

output "input_bucket_name" {
  description = "Name of the S3 bucket for input documents"
  value       = aws_s3_bucket.input_documents.id
}

output "output_bucket_name" {
  description = "Name of the S3 bucket for output results"
  value       = aws_s3_bucket.output_results.id
}

output "knowledge_base_bucket_name" {
  description = "Name of the S3 bucket for knowledge base"
  value       = aws_s3_bucket.knowledge_base.id
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.bedrock_ocr.repository_url
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.document_processor.function_name
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.bedrock_ocr.name
}

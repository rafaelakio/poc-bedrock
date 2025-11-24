terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "bedrock-ocr-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "bedrock-ocr"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# S3 Bucket para documentos de entrada
resource "aws_s3_bucket" "input_documents" {
  bucket = "${var.project_name}-input-${var.environment}"
}

resource "aws_s3_bucket_versioning" "input_documents" {
  bucket = aws_s3_bucket.input_documents.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "input_documents" {
  bucket = aws_s3_bucket.input_documents.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket para resultados
resource "aws_s3_bucket" "output_results" {
  bucket = "${var.project_name}-output-${var.environment}"
}

resource "aws_s3_bucket_versioning" "output_results" {
  bucket = aws_s3_bucket.output_results.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "output_results" {
  bucket = aws_s3_bucket.output_results.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket para base de conhecimento
resource "aws_s3_bucket" "knowledge_base" {
  bucket = "${var.project_name}-knowledge-${var.environment}"
}

resource "aws_s3_bucket_versioning" "knowledge_base" {
  bucket = aws_s3_bucket.knowledge_base.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# ECR Repository para imagem Docker
resource "aws_ecr_repository" "bedrock_ocr" {
  name                 = "${var.project_name}-${var.environment}"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster-${var.environment}"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "bedrock_ocr" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = 30
}

# IAM Role para ECS Task
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-ecs-task-execution-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM Role para ECS Task (runtime)
resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-ecs-task-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Policy para acesso ao Bedrock
resource "aws_iam_role_policy" "bedrock_access" {
  name = "bedrock-access"
  role = aws_iam_role.ecs_task.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v1"
        ]
      }
    ]
  })
}

# Policy para acesso aos buckets S3
resource "aws_iam_role_policy" "s3_access" {
  name = "s3-access"
  role = aws_iam_role.ecs_task.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.input_documents.arn,
          "${aws_s3_bucket.input_documents.arn}/*",
          aws_s3_bucket.knowledge_base.arn,
          "${aws_s3_bucket.knowledge_base.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = [
          "${aws_s3_bucket.output_results.arn}/*"
        ]
      }
    ]
  })
}

# Lambda Function para processamento
resource "aws_lambda_function" "document_processor" {
  filename      = "lambda_function.zip"
  function_name = "${var.project_name}-processor-${var.environment}"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "lambda_handler.handler"
  runtime       = "python3.11"
  timeout       = 900
  memory_size   = 2048
  
  environment {
    variables = {
      OCR_MODEL_ID        = var.ocr_model_id
      EMBEDDING_MODEL_ID  = var.embedding_model_id
      VALIDATION_MODEL_ID = var.validation_model_id
      OUTPUT_BUCKET       = aws_s3_bucket.output_results.id
      KNOWLEDGE_BUCKET    = aws_s3_bucket.knowledge_base.id
    }
  }
}

# IAM Role para Lambda
resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-execution-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_bedrock" {
  name = "bedrock-access"
  role = aws_iam_role.lambda_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.input_documents.arn,
          "${aws_s3_bucket.input_documents.arn}/*",
          aws_s3_bucket.output_results.arn,
          "${aws_s3_bucket.output_results.arn}/*",
          aws_s3_bucket.knowledge_base.arn,
          "${aws_s3_bucket.knowledge_base.arn}/*"
        ]
      }
    ]
  })
}

# S3 Event Notification para Lambda
resource "aws_s3_bucket_notification" "input_documents" {
  bucket = aws_s3_bucket.input_documents.id
  
  lambda_function {
    lambda_function_arn = aws_lambda_function.document_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".pdf"
  }
  
  lambda_function {
    lambda_function_arn = aws_lambda_function.document_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".jpg"
  }
  
  lambda_function {
    lambda_function_arn = aws_lambda_function.document_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".png"
  }
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.document_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.input_documents.arn
}

# API Gateway para interface REST
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST"]
    allow_headers = ["*"]
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  
  integration_uri    = aws_lambda_function.document_processor.invoke_arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "process" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /process"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.document_processor.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

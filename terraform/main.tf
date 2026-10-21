terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. Amazon Elastic Container Registry (ECR)
resource "aws_ecr_repository" "clinic_ecr" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project     = "Savannah Clinic Booking System"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

# 2. IAM Role for App Runner to pull container images from ECR
resource "aws_iam_role" "apprunner_ecr_role" {
  name = "AppRunnerECRAccessRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project   = "Savannah Clinic Booking System"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_role_policy_attachment" "apprunner_ecr_policy" {
  role       = aws_iam_role.apprunner_ecr_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# 3. AWS App Runner Service (Fully Managed Serverless Container Platform)
resource "aws_apprunner_service" "clinic_service" {
  service_name = var.service_name
  depends_on   = [aws_iam_role_policy_attachment.apprunner_ecr_policy]

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr_role.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.clinic_ecr.repository_url}:${var.image_tag}"
      image_repository_type = "ECR"

      image_configuration {
        port = tostring(var.port)
        runtime_environment_variables = {
          ENVIRONMENT = "production"
          PORT        = tostring(var.port)
        }
      }
    }

    auto_deployments_enabled = true
  }

  instance_configuration {
    cpu    = var.cpu
    memory = var.memory
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  tags = {
    Project     = "Savannah Clinic Booking System"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

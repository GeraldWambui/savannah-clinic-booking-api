variable "aws_region" {
  type        = string
  description = "The AWS Region where resources will be provisioned"
  default     = "us-east-1"
}

variable "service_name" {
  type        = string
  description = "Name of the AWS App Runner service"
  default     = "savannah-clinic-api"
}

variable "ecr_repo_name" {
  type        = string
  description = "Name of the Amazon Elastic Container Registry (ECR) repository"
  default     = "savannah-clinic-api"
}

variable "image_tag" {
  type        = string
  description = "Container image tag to deploy from ECR"
  default     = "latest"
}

variable "cpu" {
  type        = string
  description = "App Runner CPU allocation"
  default     = "1 vCPU"
}

variable "memory" {
  type        = string
  description = "App Runner Memory allocation"
  default     = "2 GB"
}

variable "port" {
  type        = number
  description = "Port exposed by the FastAPI container"
  default     = 8000
}
